#!/usr/bin/env python3
"""Reconcile the descriptive bottleneck audit against the frozen cohort ledgers."""
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check() -> dict:
    audit = json.loads((ROOT / "reports/historical_label_bottleneck_audit.json").read_text())
    triage = json.loads((ROOT / "reports/historical_blind_followup_triage_round1.json").read_text())
    rows = audit["rows"]
    classes = set(audit["retrieval_evidence_classes"])
    ids = [r["versioned_id"] for r in rows]
    assert len(ids) == len(set(ids)) == 13
    assert set(ids) == {r["versioned_id"] for r in triage["rows"]}
    assert all(r["retrieval_class"] in classes and r["directness_obstacle"] and r["first_next_test"] for r in rows)
    counts = Counter(r["retrieval_class"] for r in rows)
    assert all(audit["derived_counts"][name] == counts[name] for name in classes)
    assert audit["derived_counts"]["questions"] == len(rows)
    assert audit["derived_counts"]["direct_labels"] == triage["summary"]["direct_resolution_labels_authenticated"]
    return {"ok": True, "questions": len(rows), "retrieval_classes": dict(counts), "direct_labels": 0}


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
