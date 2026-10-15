#!/usr/bin/env python3
"""Run a bounded, same-oracle SQLancer/SQLite feasibility pair in Docker."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path


SQLANCER_COMMIT = "d8e6b158a1a18ab803d1c90bbbc45f58c94c60ba"
IMAGE = "maven:3.9-eclipse-temurin-21"
DEFAULT_SEED = 4101


def run(command: list[str], *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sqlancer-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/sqlancer_feasibility"))
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()
    source = args.sqlancer_source.resolve()
    jar = source / "target/sqlancer-2.0.0.jar"
    if not jar.is_file() or not (source / "target/lib").is_dir():
        raise SystemExit("SQLancer build is missing: build the pinned source first")
    commit = run(["git", "-C", str(source), "rev-parse", "HEAD"])
    if commit.returncode != 0 or commit.stdout.strip() != SQLANCER_COMMIT:
        raise SystemExit("SQLancer source revision differs from the pinned commit")
    image = run(["docker", "image", "inspect", IMAGE, "--format", "{{index .RepoDigests 0}}"])
    if image.returncode != 0:
        raise SystemExit("Maven/JDK Docker image is unavailable")

    if (args.output / "metadata.json").exists():
        raise SystemExit("output already contains a run; choose a fresh --output directory")
    args.output.mkdir(parents=True, exist_ok=True)
    metadata = {
        "study_status": "feasibility_only",
        "source_commit": SQLANCER_COMMIT,
        "jar_sha256": hashlib.sha256(jar.read_bytes()).hexdigest(),
        "container_image_digest": image.stdout.strip(),
        "oracle": "NoREC",
        "seed": args.seed,
        "query_cap": 200,
        "attempts": 1,
        "database_cap": 1,
        "conditions": [],
        "confirmed_distinct_bugs": None,
    }
    for condition, enabled in (("unguided", "false"), ("query_plan_guidance", "true")):
        run_dir = (args.output / condition).resolve()
        run_dir.mkdir(parents=True, exist_ok=True)
        cid_file = run_dir / "container.id"
        command = [
            "docker", "run", "--rm", "--network", "none", "--cpus", "1",
            "--memory", "1g", "--pids-limit", "256", "--cap-drop", "ALL",
            "--cidfile", str(cid_file),
            "--mount", f"type=bind,source={source / 'target'},target=/artifact,readonly",
            "--mount", f"type=bind,source={run_dir},target=/run",
            "--workdir", "/run", IMAGE,
            "java", "-jar", "/artifact/sqlancer-2.0.0.jar",
            "--num-threads", "1", "--random-seed", str(args.seed),
            "--num-tries", "1", "--max-generated-databases", "1", "--num-queries", "200",
            "--timeout-seconds", "30", "--print-progress-summary", "true",
            "--qpg-enable", enabled, "--qpg-log-query-plan", enabled,
            "--qpg-max-interval", "20",
            "sqlite3", "--oracle", "NoREC",
        ]
        started = time.monotonic()
        try:
            completed = run(command, timeout=90)
            outcome = {"condition": condition, "qpg_enabled": enabled == "true",
                       "exit_code": completed.returncode,
                       "elapsed_seconds": round(time.monotonic() - started, 3),
                       "stdout_file": f"{condition}/stdout.log",
                       "stderr_file": f"{condition}/stderr.log"}
            (run_dir / "stdout.log").write_text(completed.stdout)
            (run_dir / "stderr.log").write_text(completed.stderr)
        except subprocess.TimeoutExpired as error:
            if cid_file.exists():
                run(["docker", "stop", cid_file.read_text().strip()], timeout=20)
            outcome = {"condition": condition, "qpg_enabled": enabled == "true",
                       "exit_code": None, "timed_out": True,
                       "elapsed_seconds": round(time.monotonic() - started, 3),
                       "stdout_file": f"{condition}/stdout.log",
                       "stderr_file": f"{condition}/stderr.log"}
            stdout = error.stdout or ""
            stderr = error.stderr or ""
            (run_dir / "stdout.log").write_text(stdout.decode(errors="replace") if isinstance(stdout, bytes) else stdout)
            (run_dir / "stderr.log").write_text(stderr.decode(errors="replace") if isinstance(stderr, bytes) else stderr)
        current_logs = list((run_dir / "logs/sqlite3").glob("*-cur.log"))
        versions = set()
        for path in current_logs:
            match = re.search(r"^-- Database version: (.+)$", path.read_text(), re.MULTILINE)
            if match:
                versions.add(match.group(1))
        outcome["database_versions_logged"] = sorted(versions)
        outcome["database_log_count"] = len(current_logs)
        for key, pattern in (
            ("queries", r"^\s*(\d+) queries$"),
            ("databases", r"^\s*(\d+) databases$"),
            ("successful_statements", r"^\s*(\d+) successfully-executed statements$"),
            ("unsuccessful_statements", r"^\s*(\d+) unsuccess\w*-executed statements$"),
        ):
            match = re.search(pattern, (run_dir / "stdout.log").read_text(), re.MULTILINE)
            outcome[key] = int(match.group(1)) if match else None
        metadata["conditions"].append(outcome)
        (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        if outcome["exit_code"] != 0:
            raise SystemExit(f"{condition} process failed; inspect saved logs")
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
