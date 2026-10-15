#!/usr/bin/env python3
"""Audit readiness for a CS transfer without fabricating outcome forecasts."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from research_platform.opportunity import OUTCOMES, load_jsonl


candidate_registry = Path("data/research_questions.jsonl")
registry = Path("data/questions.jsonl")
candidate_count = sum(1 for line in candidate_registry.read_text().splitlines() if line.strip()) if candidate_registry.exists() else 0
records = load_jsonl(registry) if registry.exists() else []
report = {
    "status": "cs_outcome_model_unvalidated",
    "candidate_questions": candidate_count,
    "historical_question_snapshots": len(records),
    "audited_label_counts": {
        outcome: sum(record.labels is not None and outcome in record.labels for record in records)
        for outcome in OUTCOMES
    },
    "paper3_cs_forecasts": None,
    "paper4_action_rankings": None,
    "direction_value_rankings": None,
    "next_step": "Freeze source-located historical CS questions and future labels; validate Paper 3 transfer out of time before reporting probabilities. Audit action likelihoods and outcomes before ranking Paper 4 actions.",
}
output = Path("results/paper5_transfer_readiness.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
