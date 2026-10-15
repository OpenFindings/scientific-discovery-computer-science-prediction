#!/usr/bin/env python3
"""Reconcile the independently executed QAOA cycle into canonical state."""
from __future__ import annotations

import json
from pathlib import Path

from research_supervisor import append_jsonl, atomic_json, now, read_json, sync_track_checkpoints

ROOT = Path(__file__).resolve().parents[1]
REPLICATION_ID = "PAPER4-QAOA-A1-INDEPENDENT-REPLICATION-001"
FAIR_ID = "PAPER4-QAOA-FAIR-SHOT-COST-001"
REPLICATION_ARTIFACT = "results/qaoa_source_baseline_replication_20261015/result.json"
REPLICATION_VALIDATION = "reports/qaoa_independent_replication_validation_20261015.json"
FAIR_ARTIFACT = "results/qaoa_fair_cost_comparison_20261015/result.json"


def validate_replication(result: dict, validation: dict) -> tuple[bool, dict]:
    missing = []
    if not validation.get("all_checks_pass"): missing.append("independent_replication_validation")
    summary = result.get("summary", {})
    if summary.get("outcomes_retained") != 20: missing.append("20_graph_outcomes")
    if not summary.get("all_graph_feasibility"): missing.append("all_graph_feasibility")
    if not result.get("observations"): missing.append("raw_observations")
    ok = not missing
    return ok, {"mode": "experiment_result", "scientific_success": ok, "missing_or_failed": missing, "reason": "scientific criteria satisfied" if ok else "replication criteria failed"}


def validate_fair(result: dict) -> tuple[bool, dict]:
    missing = []
    if len(result.get("rows", [])) != 20: missing.append("20_graph_rows")
    for key in ("postselected_minus_standard_mean", "postselected_minus_matched_budget_standard_mean", "mean_accepted_count", "mean_discarded_count"):
        if key not in result.get("summary", {}): missing.append(key)
    if result.get("configuration", {}).get("cost_proxy") != "state preparations / measurements / retained samples": missing.append("declared_cost_proxy")
    ok = not missing
    return ok, {"mode": "experiment_result", "scientific_success": ok, "missing_or_failed": missing, "reason": "scientific criteria satisfied" if ok else "fair-cost criteria failed"}


def main() -> int:
    replication = read_json(ROOT / REPLICATION_ARTIFACT)
    replication_validation = read_json(ROOT / REPLICATION_VALIDATION)
    fair = read_json(ROOT / FAIR_ARTIFACT)
    rep_ok, rep_validation = validate_replication(replication, replication_validation)
    fair_ok, fair_validation = validate_fair(fair)
    if not (rep_ok and fair_ok):
        raise SystemExit(json.dumps({"replication": rep_validation, "fair": fair_validation}))
    state = read_json(ROOT / "research/state.json")
    queue = read_json(ROOT / "research/task_queue.json")
    rows = {task["task_id"]: task for task in queue.get("tasks", [])}
    for task_id, artifact, experiment, validation in ((REPLICATION_ID, REPLICATION_ARTIFACT, replication, rep_validation), (FAIR_ID, FAIR_ARTIFACT, fair, fair_validation)):
        task = rows.get(task_id)
        if not task:
            raise SystemExit(f"missing admitted task: {task_id}")
        task.update({"status": "completed", "attempts": 1, "started_at": task.get("started_at", now()), "finished_at": now(), "scientific_status": "scientifically_completed", "scientific_validation": validation,
                     "last_result": {"exit_code": 0, "artifact_valid": True, "scientific_success": True, "independent_validation": REPLICATION_VALIDATION if task_id == REPLICATION_ID else "inline_fair_cost_checks", "falsification_status": experiment["falsification_gate"]["status"]}})
    state.setdefault("completed_tasks", [])
    for task_id in (REPLICATION_ID, FAIR_ID):
        if task_id not in state["completed_tasks"]:
            state["completed_tasks"].append(task_id)
            state["current_research_round"] = int(state.get("current_research_round", 0)) + 1
    state["pending_tasks"] = [task["task_id"] for task in queue["tasks"] if task.get("status") in {"pending", "failed"}]
    state["blocked_tasks"] = [task["task_id"] for task in queue["tasks"] if task.get("status") == "blocked"]
    state["campaign_status"] = "waiting_for_eligible_task"
    state["current_phase"] = FAIR_ID.lower()
    state["next_action"] = "Do not claim QAOA practical advantage; require a changed protocol or renewed budget before another run."
    state["opportunity_ranking"] = []
    budget = state.setdefault("budget_consumption", {})
    budget["experiments_started"] = max(int(budget.get("experiments_started", 0)), 10)
    budget["completed_experiments"] = int(budget.get("completed_experiments", 0)) + 2
    renewal = budget.get("renewable_experiment_budget")
    if isinstance(renewal, dict):
        renewal["consumed"] = 2
        renewal["remaining"] = 0
        renewal["status"] = "EXHAUSTED"
        renewal["exhausted_at"] = now()
    state["latest_scientific_increment"] = {"kind": "independent_replication_and_fair_cost_experiment", "task_id": FAIR_ID, "scientific_success": True, "evidence_level": fair["evidence_tier"], "decision": fair["falsification_gate"]["status"], "observed_result": fair["observed_result_or_blocker"], "next_falsifiable_action": fair["next_falsifiable_action"]}
    state.setdefault("actual_experiment_results", []).extend([
        {"artifact": REPLICATION_ARTIFACT, "experiment_id": replication["experiment_id"], "evidence_level": replication["evidence_tier"], "result": replication["summary"], "limitation": "; ".join(replication["limitations"]), "falsification_outcome": replication["falsification_gate"]},
        {"artifact": FAIR_ARTIFACT, "experiment_id": fair["experiment_id"], "evidence_level": fair["evidence_tier"], "result": fair["summary"], "limitation": "; ".join(fair["limitations"]), "falsification_outcome": fair["falsification_gate"]},
    ])
    state["checkpoint_time"] = now()
    atomic_json(ROOT / "research/task_queue.json", queue)
    atomic_json(ROOT / "research/state.json", state)
    ledger = ROOT / "research/experiment_ledger.jsonl"
    existing = {json.loads(line).get("experiment_id") for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()}
    for experiment, task_id, artifact, validation in ((replication, REPLICATION_ID, REPLICATION_ARTIFACT, rep_validation), (fair, FAIR_ID, FAIR_ARTIFACT, fair_validation)):
        if experiment["experiment_id"] not in existing:
            append_jsonl(ledger, {"experiment_id": experiment["experiment_id"], "hypothesis": experiment["hypothesis"], "methodology": experiment["method"], "configuration": experiment["configuration"], "actual_result": experiment, "uncertainty": experiment["uncertainty"], "falsification_outcome": experiment["falsification_gate"], "decision": experiment["falsification_gate"]["status"], "timestamp": now(), "reproducibility_artifact": artifact, "scientific_validation": validation, "exit_code": 0})
    for task_id, experiment in ((REPLICATION_ID, replication), (FAIR_ID, fair)):
        append_jsonl(ROOT / "research/supervisor_events.jsonl", {"event": "local_experiment_scientifically_reconciled", "task_id": task_id, "experiment_id": experiment["experiment_id"], "scientific_success": True, "falsification_status": experiment["falsification_gate"]["status"], "timestamp": now()})
    supervisor = read_json(ROOT / "research/supervisor_state.json")
    sync_track_checkpoints(ROOT, state, queue, supervisor)
    print(json.dumps({"completed": [REPLICATION_ID, FAIR_ID], "round": state["current_research_round"], "scientific_success": True, "fair_cost_decision": fair["falsification_gate"]["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
