#!/usr/bin/env python3
"""Run five frozen, order-balanced SQLancer++ arms at equal cgroup CPU budgets."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import subprocess
import time
from decimal import Decimal
from pathlib import Path


SOURCE_COMMIT = "1405d4eb5b7af7a639717a47147bd89362558830"
JAR_SHA256 = "d5d342e99d9088eebadac1f13c9ffe86d7b886b75c585a8271034cedc51410be"
IMAGE_DIGEST = "maven@sha256:99e61abcff91a9b1333463bd8451fb18495d6eba9250ac66a338b518f8278320"
IMAGE = "maven:3.9-eclipse-temurin-21"
SEEDS = tuple(range(4131, 4136))
BUDGET_USEC = 4_500_000
QUERY_CAP = 200
DATABASE_SAFETY_CAP = 100
RATE_RE = re.compile(r"^Success rate for query pairs: ([0-9.]+)$", re.MULTILINE)
VERSION_RE = re.compile(r"^-- Database version: (.+)$", re.MULTILINE)


def frozen_orders() -> dict[int, tuple[str, str]]:
    flags = ["feedback_on"] * 2 + ["feedback_off"] * 3
    random.Random(4131).shuffle(flags)
    return {seed: (first, "feedback_off" if first == "feedback_on" else "feedback_on")
            for seed, first in zip(SEEDS, flags)}


def check_source(source: Path) -> dict[str, str]:
    jar = source / "target/sqlancer-2.0.0.jar"
    if not jar.is_file() or not (source / "target/lib").is_dir():
        raise RuntimeError("pinned SQLancer++ build missing")
    result = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
    if result.stdout.strip() != SOURCE_COMMIT:
        raise RuntimeError("source revision mismatch")
    image = subprocess.run(["docker", "image", "inspect", IMAGE, "--format", "{{index .RepoDigests 0}}"], capture_output=True, text=True, check=True)
    jar_hash = hashlib.sha256(jar.read_bytes()).hexdigest()
    if jar_hash != JAR_SHA256 or image.stdout.strip() != IMAGE_DIGEST:
        raise RuntimeError("pinned JAR or container image digest mismatch")
    return {"source_commit": SOURCE_COMMIT, "jar_sha256": jar_hash,
            "container_image_digest": image.stdout.strip()}


def parse_receipt(path: Path) -> dict[str, str]:
    rows = [line.split("=", 1) for line in path.read_text().splitlines()]
    receipt = dict(rows)
    required = {"start_cpu_usec", "end_cpu_usec", "used_cpu_usec", "budget_usec", "stop_reason", "child_status"}
    if set(receipt) != required:
        raise ValueError(f"malformed stop receipt: {path}")
    if int(receipt["end_cpu_usec"]) - int(receipt["start_cpu_usec"]) != int(receipt["used_cpu_usec"]):
        raise ValueError(f"inconsistent stop receipt: {path}")
    return receipt


def derive_arm(run_dir: Path, condition: str, returncode: int, elapsed: float) -> dict:
    stdout = (run_dir / "stdout.log").read_text()
    stderr = (run_dir / "stderr.log").read_text()
    receipt = parse_receipt(run_dir / "stop_receipt.txt")
    rates = [Decimal(x) for x in RATE_RE.findall(stdout)]
    counts = [rate * QUERY_CAP for rate in rates]
    if not all(count == int(count) for count in counts):
        raise ValueError(f"non-integral rate-derived count in {run_dir}")
    versions = set()
    for path in (run_dir / "logs/general").glob("*-cur.log"):
        versions.update(VERSION_RE.findall(path.read_text()))
    # The pinned StateLogger writes bug/exception traces as <database>.log;
    # *-cur.log is only the rolling SQL trace and is not evidence of a bug.
    candidate_logs = sorted(str(path.relative_to(run_dir)) for path in (run_dir / "logs/general").glob("*.log")
                            if not path.name.endswith(("-cur.log", "-plan.log", "-reduce.log")))
    used = int(receipt["used_cpu_usec"])
    return {
        "condition": condition,
        "docker_returncode": returncode,
        "wall_seconds": elapsed,
        "receipt": receipt,
        "complete_database_rates": [str(x) for x in rates],
        "complete_database_count": len(rates),
        "successful_query_pairs_in_complete_databases": sum(int(x) for x in counts),
        "database_versions_logged": sorted(versions),
        "candidate_error_logs": candidate_logs,
        "stderr_nonempty": bool(stderr.strip()),
        "cpu_overshoot_fraction": (used - BUDGET_USEC) / BUDGET_USEC,
        "counter_complete": (returncode == 0 and receipt["stop_reason"] == "cpu_budget"
                             and int(receipt["budget_usec"]) == BUDGET_USEC
                             and BUDGET_USEC <= used <= BUDGET_USEC * 1.03
                             and len(rates) >= 8 and versions == {"3.40.0"}),
    }


def run_arm(source: Path, output: Path, seed: int, condition: str) -> dict:
    run_dir = (output / str(seed) / condition).resolve()
    if run_dir.exists():
        raise RuntimeError(f"arm directory already exists; refusing overwrite: {run_dir}")
    run_dir.mkdir(parents=True)
    feedback = "true" if condition == "feedback_on" else "false"
    wrapper = Path(__file__).resolve().parent / "stop_at_cpu_budget.sh"
    cid_file = run_dir / "container.id"
    command = [
        "docker", "run", "--rm", "--network", "none", "--cpus", "1", "--memory", "1g",
        "--pids-limit", "256", "--cap-drop", "ALL", "--cidfile", str(cid_file),
        "--mount", f"type=bind,source={wrapper},target=/runner.sh,readonly",
        "--mount", f"type=bind,source={source / 'target'},target=/artifact,readonly",
        "--mount", f"type=bind,source={source / 'dbconfigs'},target=/run/dbconfigs,readonly",
        "--mount", f"type=bind,source={run_dir},target=/run", "--workdir", "/run", IMAGE,
        "bash", "/runner.sh", str(BUDGET_USEC), "java", "-jar", "/artifact/sqlancer-2.0.0.jar",
        "--num-threads", "1", "--random-seed", str(seed), "--num-tries", "1",
        "--max-generated-databases", str(DATABASE_SAFETY_CAP), "--num-queries", str(QUERY_CAP),
        "--database-prefix", condition, "--timeout-seconds", "45", "--print-progress-summary", "true",
        "general", "--database-engine", "SQLITE", "--oracle", "NOREC", "--enable-feedback", feedback,
    ]
    started = time.monotonic()
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=60, check=False)
    except subprocess.TimeoutExpired:
        if cid_file.exists():
            subprocess.run(["docker", "stop", cid_file.read_text().strip()], capture_output=True, text=True, timeout=20)
        raise
    elapsed = time.monotonic() - started
    (run_dir / "stdout.log").write_text(result.stdout)
    (run_dir / "stderr.log").write_text(result.stderr)
    arm = derive_arm(run_dir, condition, result.returncode, elapsed)
    (run_dir / "arm_summary.json").write_text(json.dumps(arm, indent=2, sort_keys=True) + "\n")
    return arm


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/sqlancerpp_feedback_equal_cpu_4131_4135"))
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"output already exists; refusing to overwrite: {output}")
    pins = check_source(source)
    output.mkdir(parents=True)
    orders = frozen_orders()
    campaign = {
        "experiment_id": "EXP-DBMS-FEEDBACK-EQUAL-CPU-4131-4135",
        "preregistration": "research/experiment_preregistration_sqlancerpp_equal_cpu_4131_4135.md",
        "budget_usec_per_arm": BUDGET_USEC,
        "query_cap_per_database": QUERY_CAP,
        "database_safety_cap": DATABASE_SAFETY_CAP,
        "orders": {str(k): list(v) for k, v in orders.items()},
        "pins": pins,
        "seed_results": [],
    }
    for seed in SEEDS:
        row = {"seed": seed, "order": list(orders[seed]), "arms": []}
        for condition in orders[seed]:
            row["arms"].append(run_arm(source, output, seed, condition))
            (output / "campaign.json").write_text(json.dumps(campaign | {"in_progress": row}, indent=2, sort_keys=True) + "\n")
        campaign["seed_results"].append(row)
        (output / "campaign.json").write_text(json.dumps(campaign, indent=2, sort_keys=True) + "\n")
        print(f"seed {seed}: " + ", ".join(f"{a['condition']}={a['successful_query_pairs_in_complete_databases']} ({a['complete_database_count']} db, {a['receipt']['used_cpu_usec']} usec)" for a in row["arms"]), flush=True)
    print(json.dumps({"completed_pairs": len(campaign["seed_results"]), "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
