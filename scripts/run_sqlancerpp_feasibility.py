#!/usr/bin/env python3
"""Run a bounded within-SQLancer++ feedback on/off operational check."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from decimal import Decimal
from pathlib import Path


SOURCE_COMMIT = "1405d4eb5b7af7a639717a47147bd89362558830"
IMAGE = "maven:3.9-eclipse-temurin-21"
DEFAULT_SEED = 4101


def run(command: list[str], *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/sqlancerpp_feasibility"))
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--database-cap", type=int, default=3)
    args = parser.parse_args()
    if args.database_cap < 1 or args.database_cap > 100:
        raise SystemExit("--database-cap must be in [1, 100]")
    source = args.source.resolve()
    jar = source / "target/sqlancer-2.0.0.jar"
    if not jar.is_file() or not (source / "target/lib").is_dir():
        raise SystemExit("Build the pinned SQLancer++ source before running")
    if not (source / "dbconfigs/disabled_options.csv").is_file() or not (source / "dbconfigs/jdbc.properties").is_file():
        raise SystemExit("SQLancer++ dbconfigs are missing")
    commit = run(["git", "-C", str(source), "rev-parse", "HEAD"])
    if commit.returncode or commit.stdout.strip() != SOURCE_COMMIT:
        raise SystemExit("SQLancer++ source revision differs from the pinned commit")
    image = run(["docker", "image", "inspect", IMAGE, "--format", "{{index .RepoDigests 0}}"])
    if image.returncode:
        raise SystemExit("Docker Maven/JDK image is unavailable")
    if (args.output / "metadata.json").exists():
        raise SystemExit("output already contains a run; choose a fresh --output directory")
    args.output.mkdir(parents=True, exist_ok=True)
    metadata = {
        "study_status": "operational_feasibility_only",
        "source_commit": SOURCE_COMMIT,
        "jar_sha256": hashlib.sha256(jar.read_bytes()).hexdigest(),
        "container_image_digest": image.stdout.strip(),
        "oracle": "NoREC",
        "database_engine": "SQLITE",
        "seed": args.seed,
        "query_cap_per_database": 200,
        "database_cap": args.database_cap,
        "learning_enabled": False,
        "conditions": [],
        "confirmed_distinct_bugs": None,
    }
    for condition, feedback in (("feedback_off", "false"), ("feedback_on", "true")):
        run_dir = (args.output / condition).resolve()
        run_dir.mkdir(parents=True, exist_ok=True)
        cid_file = run_dir / "container.id"
        command = [
            "docker", "run", "--rm", "--network", "none", "--cpus", "1",
            "--memory", "1g", "--pids-limit", "256", "--cap-drop", "ALL",
            "--cidfile", str(cid_file),
            "--mount", f"type=bind,source={source / 'target'},target=/artifact,readonly",
            "--mount", f"type=bind,source={run_dir},target=/run",
            "--mount", f"type=bind,source={source / 'dbconfigs'},target=/run/dbconfigs,readonly",
            "--workdir", "/run", IMAGE,
            "bash", "-c",
            '"$@"; status=$?; cat /sys/fs/cgroup/cpu.stat > /run/cpu.stat 2>/dev/null || true; exit "$status"',
            "cpu-accounting-wrapper", "java", "-jar", "/artifact/sqlancer-2.0.0.jar",
            "--num-threads", "1", "--random-seed", str(args.seed),
            "--num-tries", "1", "--max-generated-databases", str(args.database_cap), "--num-queries", "200",
            "--timeout-seconds", "45",
            "--print-progress-summary", "true",
            "general", "--database-engine", "SQLITE", "--oracle", "NOREC",
            "--enable-feedback", feedback,
        ]
        # SQLancer++ resolves dbconfigs relative to its working directory.
        # Each condition gets separate persisted logs and a read-only config.
        command[command.index("--timeout-seconds"):command.index("--timeout-seconds")] = [
            "--database-prefix", condition,
        ]
        started = time.monotonic()
        try:
            completed = run(command, timeout=90)
            stdout, stderr = completed.stdout, completed.stderr
            outcome = {
                "condition": condition,
                "feedback_enabled": feedback == "true",
                "exit_code": completed.returncode,
                "elapsed_seconds": round(time.monotonic() - started, 3),
            }
        except subprocess.TimeoutExpired as error:
            if cid_file.exists():
                run(["docker", "stop", cid_file.read_text().strip()], timeout=20)
            stdout = error.stdout or ""
            stderr = error.stderr or ""
            stdout = stdout.decode(errors="replace") if isinstance(stdout, bytes) else stdout
            stderr = stderr.decode(errors="replace") if isinstance(stderr, bytes) else stderr
            outcome = {
                "condition": condition,
                "feedback_enabled": feedback == "true",
                "exit_code": None,
                "timed_out": True,
                "elapsed_seconds": round(time.monotonic() - started, 3),
            }
        (run_dir / "stdout.log").write_text(stdout)
        (run_dir / "stderr.log").write_text(stderr)
        outcome["stdout_file"] = f"{condition}/stdout.log"
        outcome["stderr_file"] = f"{condition}/stderr.log"
        for key, pattern in (
            ("queries", r"^\s*(\d+) queries$"),
            ("databases", r"^\s*(\d+) databases$"),
            ("successful_statements", r"^\s*(\d+) successfully-executed statements$"),
            ("unsuccessful_statements", r"^\s*(\d+) unsuccessfuly-executed statements$"),
        ):
            match = re.search(pattern, stdout, re.MULTILINE)
            outcome[key] = int(match.group(1)) if match else None
        rates = [Decimal(value) for value in re.findall(
            r"^Success rate for query pairs: ([0-9.]+)$", stdout, re.MULTILINE)]
        counts = [rate * 200 for rate in rates]
        outcome["successful_query_pairs_from_rates"] = (
            sum(int(count) for count in counts)
            if len(counts) == outcome["databases"] and
               all(count == int(count) for count in counts) else None
        )
        versions = set()
        for path in (run_dir / "logs/general").glob("*-cur.log"):
            match = re.search(r"^-- Database version: (.+)$", path.read_text(), re.MULTILINE)
            if match:
                versions.add(match.group(1))
        outcome["database_versions_logged"] = sorted(versions)
        cpu_file = run_dir / "cpu.stat"
        cpu_stats = {}
        if cpu_file.is_file():
            for line in cpu_file.read_text().splitlines():
                parts = line.split()
                if len(parts) == 2 and parts[1].isdigit():
                    cpu_stats[parts[0]] = int(parts[1])
        outcome["container_cpu_stats"] = cpu_stats or None
        outcome["container_cpu_usage_seconds"] = round(cpu_stats["usage_usec"] / 1_000_000, 6) if "usage_usec" in cpu_stats else None
        metadata["conditions"].append(outcome)
        (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        if outcome["exit_code"] != 0:
            raise SystemExit(f"{condition} process failed; inspect saved logs")
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
