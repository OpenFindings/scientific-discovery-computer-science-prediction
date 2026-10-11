from __future__ import annotations

import json
from pathlib import Path
from typing import Union
from .benchmark import controlled_cases
from .belief import normalize, update_beliefs
from .models import Evidence, EvidenceKind
from .planner import PlannerWeights, rank_actions


def run_pilot(output: Union[str, Path], variant: str = "planner") -> dict:
    results = []
    weights = PlannerWeights() if variant == "planner" else PlannerWeights(information_gain=0, cost=0, tractability=0)
    for case in controlled_cases():
        beliefs = normalize({h.id: h.prior for h in case.question.hypotheses})
        actions = list(case.question.actions)
        selected = rank_actions(actions, beliefs, weights) if variant == "planner" else [(a, 0.0) for a in actions]
        history = []
        for action, _ in selected[:case.question.constraints["max_actions"]]:
            # Pilot observation is from the transparent benchmark oracle, not an LLM.
            outcome = "fail" if ((case.truth == "null_guard" and action.id == "test-null") or
                                  (case.truth == "off_by_one" and action.id == "test-index")) else "pass"
            evidence = Evidence(f"{case.question.id}-{action.id}", action.id, EvidenceKind.TEST_RESULT,
                                {"outcome": outcome}, "controlled-pilot", "v1", "2026-10-11", action.id)
            beliefs = update_beliefs(beliefs, action, evidence)
            history.append({"action": action.id, "outcome": outcome, "beliefs": beliefs})
        prediction = max(beliefs, key=beliefs.get)
        predicted_truth = "null_guard" if prediction == "H-null" else "off_by_one"
        results.append({"question_id": case.question.id, "truth": case.truth, "prediction": predicted_truth,
                        "resolved": predicted_truth == case.truth, "history": history})
    report = {"variant": variant, "benchmark": "controlled-pilot-v1", "results": results,
              "resolved_rate": sum(r["resolved"] for r in results) / len(results)}
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report
