#!/usr/bin/env python3
"""Run paired multi-seed operational checks, without cross-tool effect claims."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from pathlib import Path


def pair_is_complete(conditions: dict, off: str, on: str, database_cap: int) -> bool:
    """A zero-exit run is not complete unless both arms reached their cap."""
    return all(conditions[key]["databases"] == database_cap and
               all(isinstance(conditions[key].get(metric), int)
                   for metric in ("queries", "successful_statements", "unsuccessful_statements"))
               for key in (off, on))


def pair_has_databases(conditions: dict, off: str, on: str, database_cap: int) -> bool:
    return all(conditions[key]["databases"] == database_cap for key in (off, on))


def retained_sql_trace(run_dir: Path, condition: str) -> list[str] | None:
    """Read only the retained current log, ignoring headers and timing notes."""
    paths = list((run_dir / condition / "logs/general").glob("*-cur.log"))
    if len(paths) != 1:
        return None
    return [line.split("; --")[0] for line in paths[0].read_text().splitlines()[4:]]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sqlancer-source", type=Path, required=True)
    parser.add_argument("--sqlancerpp-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/dbms_guidance_campaign"))
    parser.add_argument("--first-seed", type=int, default=4101)
    parser.add_argument("--seeds", type=int, default=10)
    parser.add_argument("--resume", action="store_true", help="Reuse recorded seed outputs and recompute summary")
    args = parser.parse_args()
    if args.seeds < 2 or args.seeds > 100:
        raise SystemExit("--seeds must be in [2, 100]")
    if (args.output / "summary.json").exists() and not args.resume:
        raise SystemExit("Campaign summary already exists; choose a fresh output directory")
    args.output.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parent
    specs = (
        ("sqlancer_qpg", root / "run_sqlancer_feasibility.py", "--sqlancer-source", args.sqlancer_source,
         "unguided", "query_plan_guidance", 1),
        ("sqlancerpp_feedback", root / "run_sqlancerpp_feasibility.py", "--source", args.sqlancerpp_source,
         "feedback_off", "feedback_on", 3),
    )
    summary = {
        "study_status": "multi_seed_operational_check_not_effectiveness_test",
        "seed_policy": {"first_seed": args.first_seed, "count": args.seeds},
        "within_tool_pairs": {},
        "cross_tool_effect_comparison": None,
        "confirmed_distinct_bugs": None,
    }
    for name, script, source_flag, source, off, on, database_cap in specs:
        rows = []
        for seed in range(args.first_seed, args.first_seed + args.seeds):
            out = args.output / name / str(seed)
            if not (args.resume and (out / "metadata.json").is_file() and
                    len(json.loads((out / "metadata.json").read_text())["conditions"]) == 2):
                if (out / "metadata.json").exists():
                    raise SystemExit(f"partial run at {out}; preserve it and choose a fresh output directory")
                command = [sys.executable, str(script), source_flag, str(source),
                           "--seed", str(seed), "--output", str(out)]
                result = subprocess.run(command, capture_output=True, text=True, check=False)
                if result.returncode:
                    raise SystemExit(f"{name} seed {seed} failed: {result.stderr.strip() or result.stdout[-500:]}")
            run = json.loads((out / "metadata.json").read_text())
            if run["seed"] != seed:
                raise SystemExit(f"recorded seed mismatch at {out}")
            conditions = {row["condition"]: row for row in run["conditions"]}
            if any(conditions[key]["exit_code"] != 0 for key in (off, on)):
                raise SystemExit(f"{name} seed {seed} has failed condition; inspect {out}")
            complete = pair_is_complete(conditions, off, on, database_cap)
            operational = pair_has_databases(conditions, off, on, database_cap)
            trace_equal = None
            if name == "sqlancerpp_feedback":
                off_trace = retained_sql_trace(out, off)
                on_trace = retained_sql_trace(out, on)
                if off_trace is not None and on_trace is not None:
                    trace_equal = off_trace == on_trace
            rows.append({"seed": seed, "off": conditions[off], "on": conditions[on],
                         "complete_pair": complete, "operational_pair": operational,
                         "retained_sql_trace_equal": trace_equal})
        operational_rows = [row for row in rows if row["operational_pair"]]
        complete_rows = [row for row in rows if row["complete_pair"]]
        differences = {
            metric: [row["on"][metric] - row["off"][metric] for row in operational_rows
                     if all(isinstance(row[arm].get(metric), (int, float)) for arm in ("off", "on"))]
            for metric in ("queries", "successful_statements", "unsuccessful_statements", "elapsed_seconds")
        }
        summary["within_tool_pairs"][name] = {
            "conditions": [off, on],
            "n_seeds": len(rows),
            "n_operational_pairs": len(operational_rows),
            "n_complete_pairs": len(complete_rows),
            "incomplete_seeds": [row["seed"] for row in rows if not row["operational_pair"]],
            "unparsed_statement_seeds": [row["seed"] for row in operational_rows
                                         if not row["complete_pair"]],
            "retained_sql_trace_equal_pairs": sum(row["retained_sql_trace_equal"] is True
                                                   for row in rows),
            "rows": rows,
            "paired_differences_on_minus_off": {
                metric: {
                    "n_pairs": len(values),
                    "mean": round(statistics.mean(values), 4) if values else None,
                    "median": round(statistics.median(values), 4) if values else None,
                    "nonzero_pairs": sum(value != 0 for value in values),
                }
                for metric, values in differences.items()
            },
        }
        (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "study_status": summary["study_status"],
        "n_seeds": args.seeds,
        "within_tool_pairs": {name: {
            "n_operational_pairs": pair["n_operational_pairs"],
            "n_complete_pairs": pair["n_complete_pairs"],
            "incomplete_seeds": pair["incomplete_seeds"],
            "unparsed_statement_seeds": pair["unparsed_statement_seeds"],
            "paired_differences": pair["paired_differences_on_minus_off"],
        } for name, pair in summary["within_tool_pairs"].items()},
        "summary": str(args.output / "summary.json"),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
