#!/usr/bin/env python3
"""Admit the frozen QAOA replication cycle into the experiments track."""
from __future__ import annotations

import json
from pathlib import Path

from research_supervisor import append_jsonl, atomic_json, effective_experiment_cap, now, read_json

ROOT = Path(__file__).resolve().parents[1]
REPLICATION = {
    "task_id": "PAPER4-QAOA-A1-INDEPENDENT-REPLICATION-001",
    "research_key": "paper4_qaoa_a1_independent_replication",
    "track": "experiments",
    "objective": "Run a second predeclared n=10 QAOA A1 replication on 20 new simple 3-regular graph units using the unchanged source convention, fixed beta/gamma, lexicographic distance-ge-3 pair rule and alternating assignment; retain all graphs and report paired deltas.",
    "dependencies": ["PAPER4-QAOA-A1-LARGER-N-ROBUSTNESS-001"],
    "expected_information_gain": 0.82,
    "cost_estimate": 0.45,
    "priority": 96,
    "status": "pending",
    "attempts": 0,
    "max_attempts": 1,
    "counts_as_experiment": True,
    "scientific_completion": "experiment_result",
    "experiment_id": "EXP-PAPER4-QAOA-A1-INDEPENDENT-REPLICATION-20261015",
    "artifact": "results/qaoa_source_baseline_replication_20261015/result.json",
    "execution_command": "python3.12 scripts/run_qaoa_independent_replication.py",
    "success_criteria": ["20 new graph units retained", "all-graph feasibility reported", "paired delta and graph-level uncertainty reported", "no post-hoc parameter tuning"],
    "failure_handling": "A non-positive or infeasible independent replication is a scientific result; do not alter the seed, graph family or denominator.",
}
FAIR = {
    "task_id": "PAPER4-QAOA-FAIR-SHOT-COST-001",
    "research_key": "paper4_qaoa_fair_shot_cost_comparison",
    "track": "experiments",
    "objective": "Compare standard and postselected QAOA end-to-end under equal state-preparation and measurement budgets on the frozen independent replication graphs, with a matched accepted-shot standard reference; report discarded samples and no-acceptance failures.",
    "dependencies": [REPLICATION["task_id"]],
    "expected_information_gain": 0.9,
    "cost_estimate": 0.35,
    "priority": 97,
    "status": "pending",
    "attempts": 0,
    "max_attempts": 1,
    "counts_as_experiment": True,
    "scientific_completion": "experiment_result",
    "experiment_id": "EXP-PAPER4-QAOA-FAIR-SHOT-COST-20261015",
    "artifact": "results/qaoa_fair_cost_comparison_20261015/result.json",
    "execution_command": "python3.12 scripts/run_qaoa_fair_cost_comparison.py",
    "success_criteria": ["complete procedure scored", "equal preparation budget declared", "discarded and accepted samples retained", "conditional quality separated from end-to-end efficacy"],
    "failure_handling": "If physical runtime is not identifiable, retain the shot-count comparison and do not claim hardware speedup or quantum advantage.",
}


def main() -> int:
    state_path, queue_path = ROOT / "research/state.json", ROOT / "research/task_queue.json"
    state, queue = read_json(state_path), read_json(queue_path)
    budget = state.setdefault("budget_consumption", {})
    if effective_experiment_cap(budget) - int(budget.get("experiments_started", 0)) < 2:
        raise SystemExit("renewed experiment budget is not sufficient for this two-task cycle")
    existing = {task.get("task_id") for task in queue.get("tasks", [])}
    for task in (REPLICATION, FAIR):
        if task["task_id"] not in existing:
            queue.setdefault("tasks", []).append(task)
            append_jsonl(ROOT / "research/supervisor_events.jsonl", {"event": "scientifically_justified_task_admitted", "task_id": task["task_id"], "track": "experiments", "timestamp": now()})
    state["pending_tasks"] = [task["task_id"] for task in queue["tasks"] if task.get("status") in {"pending", "failed"}]
    state["campaign_status"] = "waiting_for_eligible_task"
    state["current_phase"] = REPLICATION["task_id"].lower()
    state["next_action"] = REPLICATION["objective"]
    state["opportunity_ranking"] = [{"task_id": task["task_id"], "track": "experiments", "score": round(task["priority"] * task["expected_information_gain"] / task["cost_estimate"], 4), "scientific_completion": task["scientific_completion"]} for task in (FAIR, REPLICATION)]
    state["checkpoint_time"] = now()
    atomic_json(queue_path, queue)
    atomic_json(state_path, state)
    print(json.dumps({"admitted": [REPLICATION["task_id"], FAIR["task_id"]], "pending": state["pending_tasks"], "budget": budget}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
