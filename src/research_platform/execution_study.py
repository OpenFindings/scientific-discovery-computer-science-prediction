"""Executable diagnostic benchmark with a pre-registered adversarial condition."""

from __future__ import annotations

import json
import math
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .belief import entropy, normalize, update_beliefs
from .executor import ExecutionResult, SafeExecutor
from .models import Action, Evidence, EvidenceKind, Hypothesis
from .planner import PlannerWeights, rank_actions, utility_breakdown


SUBJECTS = {
    "null-guard": '''\ndef transform(items, index, record):\n    return items[index] + ":" + record["value"].strip()\n''',
    "boundary": '''\ndef transform(items, index, record):\n    if record is None:\n        return "<null>"\n    return items[index + 1] + ":" + record["value"].strip()\n''',
    "none-of-the-above": '''\ndef transform(items, index, record):\n    if record is None:\n        return "<null>"\n    return record["value"].strip() + ":" + items[index]\n''',
    "context-confound": '''\ndef transform(items, index, record):\n    if record is None:\n        return "<null>"\n    if index == 0:\n        return items[1] + ":" + record["value"].strip()\n    return items[index] + ":" + record["value"].strip()\n''',
}

TRUTH = {"case-null": "H-null", "case-boundary": "H-boundary", "case-other": "H-none",
         "case-confounded": "H-none"}
HYPOTHESES = (
    Hypothesis("H-null", "Missing null guard causes the regression", 1 / 3),
    Hypothesis("H-boundary", "Off-by-one indexing causes the regression", 1 / 3),
    Hypothesis("H-none", "Neither proposed cause is sufficient", 1 / 3),
)


def _likelihoods(fail_probability: dict[str, float]) -> dict[str, dict[str, float]]:
    return {
        "fail": dict(fail_probability),
        "pass": {hypothesis: 1.0 - probability for hypothesis, probability in fail_probability.items()},
    }


ACTIONS = (
    Action("null-probe", "Check behavior for a missing record", ("H-null",), 1.0, .95,
           {"null-failure": {"H-null": .95, "H-boundary": .05, "H-none": .05},
            "pass": {"H-null": .05, "H-boundary": .95, "H-none": .95}},
           ("subject-artifact",)),
    Action("boundary-probe", "Check the final valid index", ("H-boundary",), 1.0, .95,
           {"boundary-failure": {"H-null": .05, "H-boundary": .95, "H-none": .05},
            "pass": {"H-null": .95, "H-boundary": .05, "H-none": .95}},
           ("subject-artifact",)),
    Action("alternative-probe", "Check an independent output-contract prediction", ("H-none",), 1.0, .80,
           {"boundary-signature": {"H-null": .02, "H-boundary": .93, "H-none": .03},
            "other-signature": {"H-null": .02, "H-boundary": .03, "H-none": .92},
            "pass": {"H-null": .96, "H-boundary": .04, "H-none": .05}},
           ("subject-artifact",)),
)

PROBE_RUNNER = r'''import importlib.util, json, sys
path, probe = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("subject", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
try:
    if probe == "null-probe":
        module.transform(["a", "b"], 0, None)
    elif probe == "boundary-probe":
        module.transform(["a", "b"], 1, {"value": "x"})
    elif probe == "alternative-probe":
        value = module.transform(["a", "b"], 0, {"value": "x"})
    else:
        raise ValueError("unknown registered probe")
    if probe == "boundary-probe":
        print(json.dumps({"outcome": "pass"}))
    elif probe == "alternative-probe" and value == "b:x":
        print(json.dumps({"outcome": "boundary-signature", "actual": value}))
    elif probe == "alternative-probe" and value == "x:a":
        print(json.dumps({"outcome": "other-signature", "actual": value}))
    elif probe == "alternative-probe" and value == "a:x":
        print(json.dumps({"outcome": "pass", "actual": value}))
    elif probe == "alternative-probe":
        print(json.dumps({"outcome": "other-signature", "actual": repr(value)}))
    else:
        print(json.dumps({"outcome": "pass"}))
except Exception as error:
    outcome = "null-failure" if probe == "null-probe" else "boundary-failure"
    print(json.dumps({"outcome": outcome, "exception": type(error).__name__, "detail": str(error)}))
'''


@dataclass(frozen=True)
class Task:
    id: str
    defect: str
    source: str


TASKS = tuple(Task(task_id, defect, SUBJECTS[defect]) for task_id, defect in (
    ("case-null", "null-guard"), ("case-boundary", "boundary"),
    ("case-other", "none-of-the-above"), ("case-confounded", "context-confound"),
))


def _posterior(beliefs: dict[str, float], action: Action, result: ExecutionResult,
               provenance_root: str) -> dict[str, float]:
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    evidence = Evidence(result.action_id + "-evidence", result.action_id, EvidenceKind.TEST_RESULT,
                        payload, "isolated-experiment", "execution-study-v1", "2026-10-11",
                        provenance_root, uncertainty=0.05)
    return update_beliefs(beliefs, action, evidence)


def _run_action(task_id: str, source: str, action: Action, executor: SafeExecutor) -> ExecutionResult:
    with tempfile.TemporaryDirectory(prefix="research-action-") as directory:
        root = Path(directory)
        subject_path = root / "subject.py"
        subject_path.write_text(source)
        command = [sys.executable, "-B", "-c", PROBE_RUNNER, str(subject_path), action.id]
        result = executor.run(action.id, command, str(root), sandbox_root=str(root))
        if result.exit_code != 0 or result.timed_out:
            raise RuntimeError(f"registered experiment failed to run: {result.stderr[-500:]}")
        return result


def _falsifier_action(remaining: list[Action], beliefs: dict[str, float]) -> Action:
    """Choose the available probe most likely to contradict the leading hypothesis."""
    leading = max(beliefs, key=beliefs.get)
    def challenge_probability(action: Action) -> float:
        probability = 0.0
        for likelihoods in action.expected_outcomes.values():
            alternatives = max((value for hypothesis, value in likelihoods.items()
                                if hypothesis != leading), default=0.0)
            if likelihoods.get(leading, 0.0) < alternatives * .5:
                probability += sum(beliefs.get(hypothesis, 0.0) * value
                                   for hypothesis, value in likelihoods.items())
        return probability
    return max(remaining, key=lambda action: (challenge_probability(action), action.id))


def _wilson(successes: int, n: int, z: float = 1.96) -> list[float]:
    rate = successes / n
    denominator = 1 + z * z / n
    center = (rate + z * z / (2 * n)) / denominator
    margin = z * math.sqrt(rate * (1 - rate) / n + z * z / (4 * n * n)) / denominator
    return [max(0.0, center - margin), min(1.0, center + margin)]


def _run_condition(task_id: str, source: str, condition: str, executor: SafeExecutor) -> dict[str, Any]:
    beliefs = normalize({hypothesis.id: hypothesis.prior for hypothesis in HYPOTHESES})
    available = list(ACTIONS)
    history: list[dict[str, Any]] = []
    observed_roots: set[str] = set()
    action_cap = 3
    while available and len(history) < action_cap:
        if condition == "direct":
            action = next((candidate for candidate in available if candidate.id == "null-probe"), available[0])
            challenge_target = None
            utility_details = None
        elif condition == "fixed-workflow":
            challenge_target = None
            utility_details = None
            order = ("null-probe", "boundary-probe", "alternative-probe")
            action = next(candidate for action_id in order if (candidate := next(
                (item for item in available if item.id == action_id), None)) is not None)
        elif condition == "paper4-planner":
            challenge_target = None
            action = rank_actions(available, beliefs, PlannerWeights(), observed_roots)[0][0]
            utility_details = utility_breakdown(action, beliefs, PlannerWeights(), observed_roots)
            # Offline baseline selects one next action and stops without seeing results.
        elif condition == "planner-feedback":
            challenge_target = None
            action = rank_actions(available, beliefs, PlannerWeights(), observed_roots)[0][0]
            utility_details = utility_breakdown(action, beliefs, PlannerWeights(), observed_roots)
        elif condition == "adversarial-falsification":
            challenge_target = max(beliefs, key=beliefs.get) if history else None
            if not history:
                action = rank_actions(available, beliefs, PlannerWeights(), observed_roots)[0][0]
                utility_details = utility_breakdown(action, beliefs, PlannerWeights(), observed_roots)
            else:
                action = _falsifier_action(available, beliefs)
                utility_details = None
        else:
            raise ValueError(f"unknown condition: {condition}")

        result = _run_action(task_id, source, action, executor)
        observed = json.loads(result.stdout.strip().splitlines()[-1])
        old_beliefs = beliefs.copy()
        if condition != "direct" or not history:
            beliefs = _posterior(beliefs, action, result, task_id)
        history.append({"action_id": action.id, "observed": observed, "beliefs_before": old_beliefs,
                        "beliefs_after": beliefs, "entropy_after": entropy(beliefs),
                        "falsification_target": challenge_target,
                        "utility_breakdown": utility_details,
                        "counterevidence": bool(challenge_target and
                                                beliefs.get(challenge_target, 0.0) < old_beliefs.get(challenge_target, 0.0)),
                        "duration_seconds": round(result.duration_seconds, 6),
                        "stdout": result.stdout, "stderr": result.stderr,
                        "exit_code": result.exit_code, "sandbox": result.sandbox_backend})
        available.remove(action)
        observed_roots.update(action.provenance_roots)
        if condition in {"direct", "paper4-planner"}:
            break
        if condition == "planner-feedback" and max(beliefs.values()) >= .90 and len(history) >= 2:
            break
        if (condition == "adversarial-falsification" and len(history) >= 2
                and max(beliefs.values()) >= .90 and not history[-1]["counterevidence"]):
            break
    predicted = max(beliefs, key=beliefs.get)
    confidence = beliefs[predicted]
    distinct_probe_families = len({entry["action_id"] for entry in history})
    conclusion_made = confidence >= .80
    resolved = conclusion_made and distinct_probe_families >= 2
    return {"question_id": task_id, "prediction": predicted if resolved else None,
            "provisional_prediction": predicted if conclusion_made else None,
            "posterior": beliefs, "confidence": confidence, "resolved": resolved,
            "distinct_probe_families": distinct_probe_families,
            "correct": None,
            "unsupported_conclusion": None,
            "actions": len(history), "cost": float(len(history)), "history": history}


def run_execution_study(output: str | Path, *, allow_managed_outer_sandbox: bool = False) -> dict[str, Any]:
    """Run all predeclared systems on identical executable cases and save complete traces."""
    conditions = ("direct", "fixed-workflow", "paper4-planner", "planner-feedback",
                  "adversarial-falsification")
    executor = SafeExecutor(timeout_seconds=5.0, cpu_seconds=3,
                            allow_managed_outer_sandbox=allow_managed_outer_sandbox)
    cells = []
    for task in TASKS:
        for condition in conditions:
            result = _run_condition(task.id, task.source, condition, executor)
            truth = TRUTH[task.id]
            result["correct"] = result["prediction"] == truth if result["resolved"] else None
            result["unsupported_conclusion"] = bool(
                result["provisional_prediction"] is not None and result["provisional_prediction"] != truth
            )
            cells.append({"condition": condition, "result": result})
    summaries = {}
    n = len(TASKS)
    for condition in conditions:
        records = [cell["result"] for cell in cells if cell["condition"] == condition]
        resolved_correct = sum(record["correct"] is True for record in records)
        unsupported = sum(record["unsupported_conclusion"] for record in records)
        provisional = [record for record in records if record["provisional_prediction"] is not None]
        correct_provisional = sum(record["provisional_prediction"] == TRUTH[record["question_id"]]
                                  for record in provisional)
        summaries[condition] = {
            "n_questions": n,
            "correct_resolutions": resolved_correct,
            "correct_resolution_rate": resolved_correct / n,
            "wilson_95_interval": _wilson(resolved_correct, n),
            "provisional_predictions": len(provisional),
            "correct_provisional_predictions": correct_provisional,
            "provisional_prediction_accuracy": (correct_provisional / len(provisional)
                                                if provisional else None),
            "unsupported_conclusions": unsupported,
            "unsupported_conclusion_rate": unsupported / n,
            "mean_actions": sum(record["actions"] for record in records) / n,
            "mean_cost": sum(record["cost"] for record in records) / n,
            "counterevidence_events": sum(
                event["counterevidence"] for record in records for event in record["history"]
            ),
            "question_level_results": records,
        }
    report = {
        "study_id": "P5-EXEC-FALSIFY-PILOT-001",
        "benchmark": "controlled-executable-diagnosis-v1",
        "planner_configuration": {"source": "Paper 4 configs/default.yaml",
                                  "source_url": "https://github.com/nonameisready/scientific-evidence-planner/blob/claude/evidence-planner-framework-mh6zwz/configs/default.yaml",
                                  "weights": {"information_gain": 10.0, "novelty": 1.0,
                                              "tractability": 1.0, "cost": 1.0},
                                  "novelty_estimator": "fraction of action provenance roots not yet observed",
                                  "known_subject_root": "subject-artifact"},
        "design": {"conditions": list(conditions), "tasks": [task.id for task in TASKS],
                   "max_actions": 3, "resolution_threshold": .80,
                   "minimum_distinct_probe_families_for_resolution": 2,
                   "evidence_independence_warning": "All probes exercise one subject artifact per case; posterior updates assume conditional independence and probe families are not independent source roots.",
                   "primary_outcome": "correct resolved diagnosis / all questions",
        "secondary_outcomes": ["unsupported conclusion rate", "actions", "cost"],
                   "repetitions": "one deterministic run per system-question cell"},
        "caveat": "Synthetic controlled pilot validates execution and falsification plumbing only; it is not a benchmark result for real software repositories or an LLM comparison.",
        "summaries": summaries,
    }
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report
