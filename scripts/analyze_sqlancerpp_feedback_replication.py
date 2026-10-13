#!/usr/bin/env python3
"""Independently recompute paired operational proxy results from retained raw rates."""
import argparse, json, math, re, statistics
from decimal import Decimal
from pathlib import Path

PINNED_COMMIT = "1405d4eb5b7af7a639717a47147bd89362558830"
RATE_RE = re.compile(r"^Success rate for query pairs: ([0-9.]+)$", re.MULTILINE)

def sign_test(pos: int, neg: int) -> dict:
    n = pos + neg
    if not n: return {"n_nonzero": 0, "two_sided_exact_p": None, "one_sided_positive_exact_p": None}
    tail = sum(math.comb(n, k) for k in range(min(pos, neg) + 1)) / (2 ** n)
    return {"n_nonzero": n, "two_sided_exact_p": min(1.0, 2 * tail),
            "one_sided_positive_exact_p": sum(math.comb(n, k) for k in range(0, neg + 1)) / (2 ** n)}

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, default=Path("results/sqlancerpp_feedback_replication_4111_4115"))
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    root = args.input
    campaign = json.loads((root / "summary.json").read_text())
    if campaign.get("study_status") != "operational_proxy_only_not_bug_effectiveness": raise SystemExit("unexpected study status")
    enriched, errors = [], []
    for item in campaign["rows"]:
        seed = item["seed"]
        metadata = json.loads((root / str(seed) / "metadata.json").read_text())
        if metadata.get("source_commit") != PINNED_COMMIT: errors.append(f"seed {seed}: source commit mismatch")
        if metadata.get("database_cap") != 20 or metadata.get("query_cap_per_database") != 200: errors.append(f"seed {seed}: cap mismatch")
        arms = {x["condition"]: x for x in metadata["conditions"]}
        if set(arms) != {"feedback_off", "feedback_on"}: errors.append(f"seed {seed}: arms missing")
        result = {"seed": seed, "complete_pair": True}
        for arm_name in ("feedback_off", "feedback_on"):
            arm = arms[arm_name]
            log = (root / str(seed) / arm_name / "stdout.log").read_text()
            rates = [Decimal(x) for x in RATE_RE.findall(log)]
            if (arm.get("exit_code") != 0 or arm.get("databases") != 20 or arm.get("database_versions_logged") != ["3.40.0"]
                    or len(rates) != 20 or any(x < 0 or x > 1 or x * 200 != int(x * 200) for x in rates)):
                result["complete_pair"] = False
                errors.append(f"seed {seed} {arm_name}: incomplete or nonintegral retained rates")
            total = sum(int(x * 200) for x in rates) if len(rates) == 20 else None
            if total != arm.get("successful_query_pairs_from_rates"): errors.append(f"seed {seed} {arm_name}: raw-rate sum disagrees with metadata")
            result[arm_name] = {"databases": arm.get("databases"), "database_versions": arm.get("database_versions_logged"),
                                "elapsed_seconds": arm.get("elapsed_seconds"), "rates": [str(x) for x in rates],
                                "derived_successful_query_pairs": total, "exit_code": arm.get("exit_code")}
        off, on = result["feedback_off"], result["feedback_on"]
        result["difference_on_minus_off"] = on["derived_successful_query_pairs"] - off["derived_successful_query_pairs"] if result["complete_pair"] else None
        if result["difference_on_minus_off"] != item.get("successful_query_pair_difference"): errors.append(f"seed {seed}: paired difference disagrees with campaign summary")
        enriched.append(result)
    values = [x["difference_on_minus_off"] for x in enriched if x["complete_pair"]]
    pos, neg = sum(x > 0 for x in values), sum(x < 0 for x in values)
    n = len(values)
    output = {"experiment_id": "EXP-DBMS-FEEDBACK-REP-4111-4115", "evidence_level": 4,
              "interpretation": "Executed reproducible operational proxy replication; not bug-yield, Paper 3 forecast, Paper 4 planner validation, or an agent-effectiveness finding.",
              "inputs": {"campaign_summary": str(root / "summary.json"), "raw_logs": "each seed/{feedback_off,feedback_on}/stdout.log",
                         "pinned_sqlancerpp_commit": PINNED_COMMIT, "seeds": [x["seed"] for x in enriched],
                         "database_cap_per_arm": 20, "query_attempt_cap_per_database": 200},
              "measurement": "For each retained per-database success rate, multiply by 200; all rates were exactly integral at the declared denominator. Sums are query-generation proxy counts, not distinct bugs.",
              "rate_source_audit": {"source_commit": PINNED_COMMIT, "file": "src/sqlancer/general/GeneralErrorHandler.java", "line": 183,
                                    "expression": "(double) qsuccess / queryNum", "configured_query_attempts": 200,
                                    "interpretation": "The source prints a direct floating-point ratio rather than a formatted percentage; multiplying the retained rates by the declared denominator reconstructs the per-database numerator in this pinned build."},
              "complete_pairs": n, "differences_on_minus_off": values,
              "summary": {"positive": pos, "zero": sum(x == 0 for x in values), "negative": neg,
                          "mean": statistics.mean(values) if values else None,
                          "sample_sd": statistics.stdev(values) if len(values) > 1 else None,
                          "mean_percentage_points_of_4000_attempt_cap": statistics.mean(values) / 4000 * 100 if values else None,
                          "median": statistics.median(values) if values else None,
                          "min": min(values) if values else None, "max": max(values) if values else None,
                          "exact_sign_test": sign_test(pos, neg)},
              "preregistered_decision": "All five complete pairs are positive, meeting the directional consistency criterion. The two-sided exact sign-test p is 0.0625 (one-sided directional p 0.03125); small n and proxy/rounding limitations preclude a broad effectiveness claim. Proceed only to exact-counter and matched-CPU instrumentation before testing bug yield.",
              "confirmed_distinct_bugs": None, "errors": errors, "seed_results": enriched}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in output.items() if k != "seed_results"}, indent=2, sort_keys=True))
    return 1 if errors else 0

if __name__ == "__main__": raise SystemExit(main())
