#!/usr/bin/env python3
"""Run repeated bounded SQLancer++ feedback checks after the short-run null."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/sqlancerpp_feedback_long_campaign"))
    parser.add_argument("--first-seed", type=int, default=4101)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--database-cap", type=int, default=20)
    args = parser.parse_args()
    if args.seeds < 2 or args.seeds > 20:
        raise SystemExit("--seeds must be in [2, 20]")
    if args.database_cap < 4 or args.database_cap > 100:
        raise SystemExit("--database-cap must be in [4, 100]")
    if (args.output / "summary.json").exists():
        raise SystemExit("summary already exists; choose a fresh output directory")
    args.output.mkdir(parents=True, exist_ok=True)
    runner = Path(__file__).resolve().parent / "run_sqlancerpp_feasibility.py"
    rows = []
    for seed in range(args.first_seed, args.first_seed + args.seeds):
        out = args.output / str(seed)
        command = [sys.executable, str(runner), "--source", str(args.source),
                   "--output", str(out), "--seed", str(seed),
                   "--database-cap", str(args.database_cap)]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode:
            raise SystemExit(f"seed {seed} failed; inspect {out}: {result.stderr.strip()}")
        run = json.loads((out / "metadata.json").read_text())
        conditions = {row["condition"]: row for row in run["conditions"]}
        off, on = conditions["feedback_off"], conditions["feedback_on"]
        complete = all(arm["exit_code"] == 0 and arm["databases"] == args.database_cap and
                       isinstance(arm["successful_query_pairs_from_rates"], int)
                       for arm in (off, on))
        rows.append({"seed": seed, "complete_pair": complete,
                     "off": off, "on": on,
                     "successful_query_pair_difference": (
                         on["successful_query_pairs_from_rates"] -
                         off["successful_query_pairs_from_rates"] if complete else None)})
        (args.output / "summary.json").write_text(json.dumps({
            "study_status": "operational_proxy_only_not_bug_effectiveness",
            "database_cap": args.database_cap,
            "query_cap_per_database": 200,
            "rows": rows,
        }, indent=2, sort_keys=True) + "\n")
    differences = [row["successful_query_pair_difference"] for row in rows if row["complete_pair"]]
    summary = {
        "study_status": "operational_proxy_only_not_bug_effectiveness",
        "database_cap": args.database_cap,
        "query_cap_per_database": 200,
        "n_seeds": len(rows),
        "n_complete_pairs": len(differences),
        "incomplete_seeds": [row["seed"] for row in rows if not row["complete_pair"]],
        "paired_query_difference_on_minus_off": {
            "values": differences,
            "mean": round(statistics.mean(differences), 3) if differences else None,
            "median": statistics.median(differences) if differences else None,
            "positive_pairs": sum(value > 0 for value in differences),
            "zero_pairs": sum(value == 0 for value in differences),
            "negative_pairs": sum(value < 0 for value in differences),
        },
        "confirmed_distinct_bugs": None,
        "rows": rows,
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in summary.items() if key != "rows"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
