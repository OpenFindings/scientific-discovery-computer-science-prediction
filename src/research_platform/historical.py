"""Leakage-safe, dependency-free historical evaluation helpers."""
from __future__ import annotations

from collections import defaultdict
from .opportunity import QuestionRecord, evaluate


def grouped_temporal_split(records: list[QuestionRecord], train_cutoff: str) -> tuple[list[QuestionRecord], list[QuestionRecord]]:
    """Split by date and question ID, never by a repeated snapshot row."""
    before = [record for record in records if record.cutoff_date <= train_cutoff]
    after = [record for record in records if record.cutoff_date > train_cutoff]
    train_ids = {record.id for record in before}
    after = [record for record in after if record.id not in train_ids]
    return before, after


def snapshot_report(records: list[QuestionRecord], cutoffs: list[str]) -> dict:
    report = {"status": "no future labels" if not any(record.labels for record in records) else "audited",
              "snapshots": []}
    for cutoff in cutoffs:
        snapshot = [record for record in records if record.cutoff_date <= cutoff]
        report["snapshots"].append({"cutoff": cutoff, "n": len(snapshot),
                                    "outcomes": {outcome: evaluate(snapshot, outcome)
                                                  for outcome in ("attention", "resolution", "premise_revision")}})
    return report
