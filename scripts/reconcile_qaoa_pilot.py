#!/usr/bin/env python3
"""Supervisor-owned reconciliation for the already executed local Paper 4 pilot."""
from __future__ import annotations

import json
from pathlib import Path

from research_supervisor import (
    append_jsonl,
    atomic_json,
    now,
    read_json,
    scientific_validation,
    sync_track_checkpoints,
)


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "PAPER4-QAOA-POSTSELECTION-PILOT-001"
ARTIFACT = "results/qaoa_postselection_pilot_20261015/result.json"
VALIDATION = "reports/paper4_qaoa_postselection_validation_20261015.json"


def main() -> int:
    result = read_json(ROOT / ARTIFACT)
    validation = read_json(ROOT / VALIDATION)
    if not validation.get("all_checks_pass"):
        raise SystemExit("independent QAOA validation did not pass")
    task = {
        "task_id": TASK_ID,
        "research_key": "paper4_qaoa_postselection_pilot",
        "track": "experiments",
        "objective": "Execute the frozen Paper 4 A2 QAOA postselection pilot and preserve the A2 setup-feasibility result plus the conditional A1 baseline.",
        "dependencies": ["PAPER4-ACTION-OUTCOME-AUDIT-001"],
        "expected_information_gain": 0.55,
        "cost_estimate": 0.2,
        "priority": 84,
        "status": "completed",
        "attempts": 1,
        "max_attempts": 1,
        "counts_as_experiment": True,
        "scientific_completion": "experiment_result",
        "experiment_id": result["experiment_id"],
        "artifact": ARTIFACT,
        "execution_command": "python3.12 scripts/run_qaoa_postselection_pilot.py",
        "success_criteria": ["frozen plan hash verified", "A2 setup feasibility measured", "A1 denominator and limitations preserved"],
        "started_at": now(),
        "finished_at": now(),
    }
    ok, scientific = scientific_validation(task, result)
    if not ok:
        raise SystemExit(json.dumps(scientific, ensure_ascii=False))
    state = read_json(ROOT / "research/state.json")
    queue = read_json(ROOT / "research/task_queue.json")
    existing = {row.get("task_id") for row in queue.get("tasks", [])}
    if TASK_ID not in existing:
        queue["tasks"].append(task)
    else:
        for row in queue["tasks"]:
            if row.get("task_id") == TASK_ID:
                row.update(task)
    row = next(row for row in queue["tasks"] if row.get("task_id") == TASK_ID)
    row["scientific_status"] = "scientifically_completed"
    row["scientific_validation"] = scientific
    row["last_result"] = {
        "exit_code": 0,
        "artifact_valid": True,
        "scientific_success": True,
        "independent_validation": VALIDATION,
        "falsification_status": result["falsification_gate"]["status"],
    }
    state.setdefault("completed_tasks", [])
    if TASK_ID not in state["completed_tasks"]:
        state["completed_tasks"].append(TASK_ID)
        state["current_research_round"] = int(state.get("current_research_round", 0)) + 1
    state["blocked_tasks"] = [x for x in state.get("blocked_tasks", []) if x != TASK_ID]
    state["pending_tasks"] = [x["task_id"] for x in queue["tasks"] if x.get("status") in {"pending", "failed"}]
    state["campaign_status"] = "waiting_for_next_activation"
    state["current_phase"] = TASK_ID.lower()
    state["next_action"] = result["next_falsifiable_action"]
    state["latest_scientific_increment"] = {
        "kind": "local_exact_state_vector_experiment",
        "task_id": TASK_ID,
        "scientific_success": True,
        "evidence_level": result["evidence_tier"],
        "decision": result["falsification_gate"]["status"],
        "observed_result": result["observed_result_or_blocker"],
        "independent_validation": VALIDATION,
        "next_falsifiable_action": result["next_falsifiable_action"],
    }
    actual = {
        "artifact": ARTIFACT,
        "evidence_level": result["evidence_tier"],
        "experiment_id": result["experiment_id"],
        "limitation": "; ".join(result["limitations"]),
        "result": result["observed_result_or_blocker"],
        "falsification_outcome": result["falsification_gate"],
    }
    results = state.setdefault("actual_experiment_results", [])
    results[:] = [x for x in results if x.get("experiment_id") != result["experiment_id"]]
    results.append(actual)
    state["opportunity_ranking"] = []
    state["checkpoint_time"] = now()
    atomic_json(ROOT / "research/task_queue.json", queue)
    atomic_json(ROOT / "research/state.json", state)
    ledger = ROOT / "research/experiment_ledger.jsonl"
    prior = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not any(x.get("experiment_id") == result["experiment_id"] for x in prior):
        append_jsonl(ledger, {
            "experiment_id": result["experiment_id"],
            "hypothesis_id": "PAPER4-A2-ALTERNATIVE-POSTSELECTION",
            "domain": "QAOA / MaxCut",
            "question": task["objective"],
            "prior_evidence": "reports/paper4_prospective_plan_v1.json",
            "methodology": result["method"],
            "configuration": result["configuration"],
            "actual_result": result,
            "uncertainty": result["uncertainty"],
            "falsification_outcome": result["falsification_gate"],
            "decision": "retain_A2_setup_no_go_and_A1_conditional_baseline",
            "timestamp": now(),
            "reproducibility_artifact": ARTIFACT,
            "independent_validation": VALIDATION,
            "exit_code": 0,
        })
    append_jsonl(ROOT / "research/supervisor_events.jsonl", {
        "event": "local_experiment_independently_validated",
        "task_id": TASK_ID,
        "experiment_id": result["experiment_id"],
        "scientific_success": True,
        "falsification_status": result["falsification_gate"]["status"],
        "timestamp": now(),
    })
    supervisor = read_json(ROOT / "research/supervisor_state.json")
    sync_track_checkpoints(ROOT, state, queue, supervisor)
    print(json.dumps({"task_id": TASK_ID, "scientific_success": True, "status": result["falsification_gate"]["status"], "round": state["current_research_round"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
