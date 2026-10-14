#!/usr/bin/env python3
"""Independently reparse frozen equal-CPU SQLancer++ logs and receipts."""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
from decimal import Decimal
from pathlib import Path


SEEDS = tuple(range(4131, 4136))
ORDERS = {
    4131: ("feedback_off", "feedback_on"),
    4132: ("feedback_off", "feedback_on"),
    4133: ("feedback_on", "feedback_off"),
    4134: ("feedback_off", "feedback_on"),
    4135: ("feedback_on", "feedback_off"),
}
BUDGET = 4_500_000
COMMIT = "1405d4eb5b7af7a639717a47147bd89362558830"
JAR_SHA = "d5d342e99d9088eebadac1f13c9ffe86d7b886b75c585a8271034cedc51410be"
IMAGE_DIGEST = "maven@sha256:99e61abcff91a9b1333463bd8451fb18495d6eba9250ac66a338b518f8278320"
RATE = re.compile(r"^Success rate for query pairs: ([0-9.]+)$", re.MULTILINE)
MISMATCH = re.compile(r"AssertionError|result sets mismatch|incorrect result", re.IGNORECASE)
VERSION = re.compile(r"^-- Database version: (.+)$", re.MULTILINE)


def exact_sign_test(values: list[int]) -> dict:
    positive = sum(value > 0 for value in values)
    negative = sum(value < 0 for value in values)
    n = positive + negative
    if n == 0:
        return {"n_nonzero": 0, "two_sided_p": None}
    tail = sum(math.comb(n, k) for k in range(min(positive, negative) + 1)) / 2**n
    return {"n_nonzero": n, "two_sided_p": min(1.0, 2 * tail)}


def parse_arm(root: Path, seed: int, condition: str) -> dict:
    directory = root / str(seed) / condition
    stdout = (directory / "stdout.log").read_text()
    stderr = (directory / "stderr.log").read_text()
    pairs = [Decimal(rate) * 200 for rate in RATE.findall(stdout)]
    if any(count != int(count) or count < 0 or count > 200 for count in pairs):
        raise ValueError(f"invalid per-database query pair rates in {directory}")
    receipt = dict(line.split("=", 1) for line in (directory / "stop_receipt.txt").read_text().splitlines())
    used = int(receipt["used_cpu_usec"])
    if int(receipt["end_cpu_usec"]) - int(receipt["start_cpu_usec"]) != used:
        raise ValueError(f"CPU receipt inconsistent in {directory}")
    stats = dict(line.split() for line in (directory / "cpu.stat").read_text().splitlines() if len(line.split()) == 2)
    # cpu.stat is captured just after the receipt's end sample and may exceed it slightly.
    if int(stats["usage_usec"]) < int(receipt["end_cpu_usec"]):
        raise ValueError(f"final cpu.stat precedes receipt in {directory}")
    versions = sorted({version for path in (directory / "logs/general").glob("*-cur.log")
                       for version in VERSION.findall(path.read_text())})
    error_logs = sorted(str(path.relative_to(directory)) for path in (directory / "logs/general").glob("*.log")
                        if not path.name.endswith(("-cur.log", "-plan.log", "-reduce.log")))
    complete = (receipt["stop_reason"] == "cpu_budget" and int(receipt["budget_usec"]) == BUDGET
                and BUDGET <= used <= BUDGET * 1.03 and len(pairs) >= 8 and versions == ["3.40.0"])
    return {
        "condition": condition,
        "complete": complete,
        "used_cpu_usec": used,
        "cpu_overshoot_fraction": (used - BUDGET) / BUDGET,
        "complete_databases": len(pairs),
        "successful_pairs_in_complete_databases": sum(int(count) for count in pairs),
        "raw_success_rates": [str(count / 200) for count in pairs],
        "version_logs": versions,
        "candidate_error_logs": error_logs,
        "stderr_nonempty": bool(stderr.strip()),
        "mismatch_marker_in_stdout_or_stderr": bool(MISMATCH.search(stdout + stderr)),
        "discarded_partial_database": "possible; no partial success count in pinned rate logger",
    }


def analyze(root: Path) -> dict:
    campaign = json.loads((root / "campaign.json").read_text())
    if campaign["experiment_id"] != "EXP-DBMS-FEEDBACK-EQUAL-CPU-4131-4135":
        raise ValueError("wrong study ID")
    if campaign["budget_usec_per_arm"] != BUDGET or campaign["query_cap_per_database"] != 200:
        raise ValueError("budget or query cap mismatch")
    if campaign["pins"] != {"source_commit": COMMIT, "jar_sha256": JAR_SHA, "container_image_digest": IMAGE_DIGEST}:
        raise ValueError("source/build/image pin mismatch")
    if len(campaign["seed_results"]) != len(SEEDS):
        raise ValueError("incomplete seed list")
    rows = []
    for expected_seed, stored in zip(SEEDS, campaign["seed_results"]):
        if stored["seed"] != expected_seed or tuple(stored["order"]) != ORDERS[expected_seed]:
            raise ValueError(f"seed or order mismatch at {expected_seed}")
        if len(stored["arms"]) != 2 or tuple(x["condition"] for x in stored["arms"]) != ORDERS[expected_seed]:
            raise ValueError(f"stored arm order mismatch at {expected_seed}")
        arms = {name: parse_arm(root, expected_seed, name) for name in ORDERS[expected_seed]}
        for saved in stored["arms"]:
            actual = arms[saved["condition"]]
            if (saved["successful_query_pairs_in_complete_databases"] != actual["successful_pairs_in_complete_databases"]
                    or saved["complete_database_count"] != actual["complete_databases"]
                    or int(saved["receipt"]["used_cpu_usec"]) != actual["used_cpu_usec"]):
                raise ValueError(f"stored counter mismatch at {expected_seed} {saved['condition']}")
        rows.append({
            "seed": expected_seed,
            "first_arm": ORDERS[expected_seed][0],
            "pair_complete": all(arm["complete"] for arm in arms.values()),
            "feedback_off": arms["feedback_off"],
            "feedback_on": arms["feedback_on"],
            "secondary_difference_on_minus_off": arms["feedback_on"]["successful_pairs_in_complete_databases"] - arms["feedback_off"]["successful_pairs_in_complete_databases"],
        })
    complete_rows = [row for row in rows if row["pair_complete"]]
    differences = [row["secondary_difference_on_minus_off"] for row in complete_rows]
    candidates = [(row["seed"], name, arm["candidate_error_logs"]) for row in rows
                  for name in ("feedback_off", "feedback_on") for arm in [row[name]]
                  if arm["candidate_error_logs"] or arm["mismatch_marker_in_stdout_or_stderr"] or arm["stderr_nonempty"]]
    return {
        "experiment_id": campaign["experiment_id"],
        "preregistration": campaign["preregistration"],
        "primary_confirmed_distinct_norec_bugs": 0 if len(complete_rows) == len(SEEDS) and not candidates else None,
        "bug_candidate_signals": candidates,
        "complete_pairs": len(complete_rows),
        "secondary_successful_pair_differences_on_minus_off": differences,
        "secondary_mean_difference": statistics.mean(differences) if differences else None,
        "secondary_median_difference": statistics.median(differences) if differences else None,
        "secondary_positive_pairs": sum(x > 0 for x in differences),
        "secondary_negative_pairs": sum(x < 0 for x in differences),
        "secondary_sign_test": exact_sign_test(differences),
        "rows": rows,
        "interpretation": "No NoREC mismatch candidate was logged in ten bounded arms; zero observed confirmed distinct bugs gives no evidence of bug-yield benefit. Four of five secondary complete-database query-pair differences were positive; this proxy is not bug yield, and the pairwise sign evidence is weak.",
        "limitations": [
            "Each arm stopped just after the 4.5-second cgroup CPU threshold; observed overshoot is retained, not silently normalized away.",
            "The interrupted database's partial query attempts have no rate-derived success count and are excluded. Complete database counts differ between arms.",
            "Only five fresh paired seeds; low power for rare reproducible bugs and for a two-sided sign test.",
            "No mismatch candidates means no blinded candidate reruns were possible; the primary zero is observed within this bounded run only.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("results/sqlancerpp_feedback_equal_cpu_4131_4135"))
    parser.add_argument("--output", type=Path, default=Path("results/sqlancerpp_feedback_equal_cpu_4131_4135/independent_analysis.json"))
    args = parser.parse_args()
    result = analyze(args.input)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "rows"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
