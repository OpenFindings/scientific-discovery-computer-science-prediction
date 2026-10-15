#!/usr/bin/env python3
"""Independently validate the additive Paper 3 observability round-3 artifact."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/historical_observable_cohort_round3.json"
FRAME = ROOT / "data/historical_cs_year_topic_frame.jsonl"
OLD = ROOT / "data/historical_cs_blind_cohort_20.jsonl"
OBS = ROOT / "data/historical_cs_observable_cohort_16.jsonl"
OUT = ROOT / "reports/paper3_round3_independent_validation.json"


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    frame = {row["versioned_id"]: row for row in rows(FRAME)}
    excluded = {row["arxiv_id"] for row in rows(OLD) + rows(OBS)} | {
        "2006.15074", "2012.08387", "2101.11149", "2112.15485"
    }
    selected = report["cohort"]["selected_rows"]
    checks: dict[str, bool] = {}
    checks["report_schema"] = all(key in report for key in ("cohort", "method", "observed_result", "paper3_gate"))
    checks["four_source_rows"] = len(selected) == 4
    checks["no_overlap_with_frozen_cohorts"] = all(row["arxiv_id"] not in excluded for row in selected)
    checks["frame_provenance_matches"] = all(
        row["versioned_id"] in frame
        and frame[row["versioned_id"]]["arxiv_id"] == row["arxiv_id"]
        and frame[row["versioned_id"]]["updated"] <= row["as_of"]
        for row in selected
    )
    checks["cutoff_years_are_in_declared_frame"] = all(
        row["as_of"][:4] in {"2017", "2018", "2019", "2020"} for row in selected
    )
    checks["no_direct_labels_claimed"] = (
        report["observed_result"]["direct_resolution_positive"] == 0
        and report["observed_result"]["direct_resolution_negative"] == 0
        and report["paper3_gate"]["status"] == "gated_no_score"
    )
    checks["ineligible_row_stays_in_denominator"] = (
        report["observed_result"]["selected_rows"] == 4
        and report["observed_result"]["source_eligible_questions"] == 3
    )
    checks["partial_progress_not_promoted"] = all(
        row["followup_audit"].get("unadjudicated_direct_outcome") is True
        for row in selected if row["source_screen"].get("status") == "eligible_source_open"
    )
    result = {
        "report": str(REPORT.relative_to(ROOT)),
        "validation": "independent_supervisor_reconciliation",
        "checks": checks,
        "all_checks_passed": all(checks.values()),
        "artifact_sha256": hashlib.sha256(REPORT.read_bytes()).hexdigest(),
        "scientific_interpretation": {
            "source_rows": 4,
            "eligible_questions": 3,
            "direct_positive": 0,
            "direct_negative": 0,
            "partial_progress": 1,
            "paper3_score": "not estimable",
            "boundary": "missing or unadjudicated outcomes are not negative labels"
        }
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["all_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
