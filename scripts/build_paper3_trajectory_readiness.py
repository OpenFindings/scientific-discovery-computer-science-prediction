#!/usr/bin/env python3
"""Audit whether the observable trajectory cohort can support Paper 3 scoring."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = [
    "direct_scientific_resolution",
    "premise_refutation_or_revision",
    "partial_progress",
    "independent_evidence_strengthening",
    "contradictory_evidence",
    "scope_narrowing_or_reformulation",
    "continued_explicit_uncertainty",
]


def main() -> int:
    source = ROOT / "reports/historical_evidence_trajectory_round2.json"
    dataset = json.loads(source.read_text())
    rows = dataset["rows"]
    counts = {}
    for dimension in DIMENSIONS:
        counts[dimension] = {
            "supported": sum(r["dimensions"][dimension] == "supported" for r in rows),
            "contradicted": sum(r["dimensions"][dimension] == "contradicted" for r in rows),
            "not_observed_after_bounded_search": sum(r["dimensions"][dimension] == "not_observed_after_bounded_search" for r in rows),
            "not_assessable": sum(r["dimensions"][dimension] == "not_assessable" for r in rows),
        }
    direct = counts["direct_scientific_resolution"]
    report = {
        "report_id": "PAPER3-TRAJECTORY-READINESS-2026-10-15",
        "methodology": "docs/paper3_methodology.md",
        "trajectory_dataset": str(source.relative_to(ROOT)),
        "feature_freeze": {
            "status": "source_and_cutoff_features_frozen_for_readiness_audit_only",
            "features_allowed": ["source-version publication date", "source-defined question text", "source-defined object/comparator/metric/gate", "topic/year stratum from frozen cohort frame"],
            "future_text_or_outcome_features_used": False,
            "model_fit_performed": False,
        },
        "outcome_counts": counts,
        "class_power_gate": {
            "direct_resolution_supported": direct["supported"],
            "direct_resolution_contradicted": direct["contradicted"],
            "direct_resolution_assessable_positive_or_negative": direct["supported"] + direct["contradicted"],
            "required_for_score": "nonzero positive and negative direct labels in grouped chronological training and untouched test periods, with prespecified minimum units and uncertainty analysis",
            "passed": False,
        },
        "temporal_split_audit": {
            "chronological_grouped_holdout_constructed": False,
            "reason": "All 12 direct outcomes are unadjudicated; not-observed-after-search is missingness, not a negative class. A temporal split would therefore contain no valid direct-outcome contrast.",
            "untouched_final_test_period": "reserved; no valid labels yet",
        },
        "decision": "no_paper3_score",
        "scientific_result": "The separate trajectory rubric produces measurable partial-progress (5) and scope-narrowing (3) records, but zero direct-resolution positives or negatives. Paper 3 transfer is not statistically or scientifically identifiable from this cohort yet.",
        "required_next_data": [
            "Directly matched future resolution or refutation under the frozen question definitions",
            "Independent negative/direct non-resolution evidence only if it is an explicit adjudicated outcome, never a failed search",
            "Enough grouped question units across early training and later untouched test periods for ranking/calibration uncertainty",
        ],
        "negative_result": "No AUC, calibration, ranking score or breakthrough probability is reported. Dimension prevalence is not estimated from this selected cohort.",
    }
    output = ROOT / "reports/paper3_trajectory_readiness.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"decision": report["decision"], "rows": len(rows), "direct_supported": direct["supported"], "direct_contradicted": direct["contradicted"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
