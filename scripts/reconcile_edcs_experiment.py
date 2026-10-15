#!/usr/bin/env python3
"""Reconcile the single authorized EDCS experiment into canonical state."""
from __future__ import annotations

import json
from pathlib import Path

from research_supervisor import append_jsonl, atomic_json, now, read_json, sync_track_checkpoints

ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "NOVEL-EDCS-LAZY-REPAIR-EXPERIMENT-001"
EXPERIMENT_ID = "EXP-EDCS-LAZY-REPAIR-INVARIANT-20261015"
ARTIFACT = "reports/edcs_experiment_result_20261015.json"
RAW_RESULT = "results/edcs_lazy_repair_counterexample_20261015/result.json"
VALIDATION = "results/edcs_lazy_repair_counterexample_20261015/independent_validation.json"


def main() -> int:
    report = read_json(ROOT / ARTIFACT)
    raw = read_json(ROOT / RAW_RESULT)
    validation = read_json(ROOT / VALIDATION)
    if report.get("experiment_id") != EXPERIMENT_ID or raw.get("experiment_id") != EXPERIMENT_ID:
        raise SystemExit("experiment identity mismatch")
    if not validation.get("scientific_success"):
        raise SystemExit("independent validation did not pass")
    if report.get("method", {}).get("implementation_sha256") != raw.get("implementation_sha256"):
        raise SystemExit("implementation hash mismatch")
    queue = read_json(ROOT / "research/task_queue.json")
    tasks = {task.get("task_id"): task for task in queue.get("tasks", [])}
    task = tasks.get(TASK_ID)
    if not task:
        raise SystemExit(f"missing task: {TASK_ID}")
    task.update({
        # The scientific gate must read the structured report, not the compact
        # runner result. Keep the raw result explicitly linked below.
        "artifact": ARTIFACT,
        "status": "completed",
        "attempts": 1,
        "finished_at": now(),
        "scientific_completion": "experiment_result",
        "scientific_status": "scientifically_completed",
        "failure_note": None,
        "scientific_validation": {
            "mode": "experiment_result",
            "scientific_success": True,
            "missing_or_failed": [],
            "reason": "finite variant counterexample independently reproduced and minimized",
        },
        "last_result": {
            "exit_code": 0,
            "artifact_valid": True,
            "scientific_success": True,
            "falsification_status": report["falsification_gate"]["status"],
            "independent_validation": VALIDATION,
            "raw_result": RAW_RESULT,
            "scientific_report": ARTIFACT,
        },
    })
    task.pop("failure_note", None)
    state = read_json(ROOT / "research/state.json")
    if TASK_ID not in state.setdefault("completed_tasks", []):
        state["completed_tasks"].append(TASK_ID)
        state["current_research_round"] = int(state.get("current_research_round", 0)) + 1
        budget = state.setdefault("budget_consumption", {})
        budget["experiments_started"] = int(budget.get("experiments_started", 0)) + 1
        budget["completed_experiments"] = int(budget.get("completed_experiments", 0)) + 1
    state["blocked_tasks"] = [t["task_id"] for t in queue["tasks"] if t.get("status") == "blocked" and t["task_id"] != TASK_ID]
    state["pending_tasks"] = [t["task_id"] for t in queue["tasks"] if t.get("status") in {"pending", "failed"}]
    state["campaign_status"] = "waiting_for_eligible_task"
    state["current_phase"] = TASK_ID.lower()
    state["idle_reason"] = "single_authorized_edcs_experiment_consumed_no_further_experiment_execution"
    state["next_action"] = "Stop experimental execution for this authorization cycle; preserve the EDCS variant counterexample and Paper 3 no-score state. Any revised repair rule requires a new protocol and explicit authorization."
    state["opportunity_ranking"] = []
    state["current_best_opportunities"] = [
        {
            "id": "EDCS-LAZY-REPAIR-INVARIANT-001",
            "status": "temporarily_closed_variant_falsified",
            "reason": "finite P1 counterexample verified for the frozen one-flip lazy variant; no revised experiment authorized",
        },
        {
            "id": "PAPER3-TARGET-B-EVIDENCE-GROWTH",
            "status": "frozen_no_score_until_labels",
            "reason": "Target B protocol is frozen, but no valid historical forecast labels are available",
        },
    ]
    state["latest_scientific_increment"] = {
        "kind": "independently_verified_finite_variant_counterexample",
        "task_id": TASK_ID,
        "scientific_success": True,
        "evidence_level": report["evidence_tier"],
        "decision": report["falsification_gate"]["status"],
        "observed_result": report["observed_result_or_blocker"],
        "next_falsifiable_action": state["next_action"],
    }
    actual_results = state.setdefault("actual_experiment_results", [])
    actual_results[:] = [row for row in actual_results if row.get("artifact") != ARTIFACT]
    actual_results.append({
        "artifact": ARTIFACT,
        "experiment_id": EXPERIMENT_ID,
        "evidence_level": report["evidence_tier"],
        "result": report["summary"],
        "limitation": "; ".join(report["limitations"]),
        "falsification_outcome": report["falsification_gate"],
    })
    audits = state.setdefault("scientific_artifact_audits", [])
    audits[:] = [row for row in audits if row.get("artifact") != ARTIFACT]
    audits.append({
        "artifact": ARTIFACT,
        "task_id": TASK_ID,
        "evidence_level": report["evidence_tier"],
        "scientific_success": True,
        "scientific_validation": task["scientific_validation"],
        "observed_result_or_blocker": report["observed_result_or_blocker"],
        "uncertainty": report["uncertainty"],
        "next_falsifiable_action": state["next_action"],
        "timestamp": now(),
    })
    state["checkpoint_time"] = now()
    atomic_json(ROOT / "research/task_queue.json", queue)
    atomic_json(ROOT / "research/state.json", state)
    ledger = ROOT / "research/experiment_ledger.jsonl"
    existing = {json.loads(line).get("experiment_id") for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()}
    if EXPERIMENT_ID not in existing:
        append_jsonl(ledger, {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis": report["hypothesis"],
            "methodology": report["method"],
            "configuration": report["configuration"],
            "actual_result": report["summary"],
            "uncertainty": report["uncertainty"],
            "falsification_outcome": report["falsification_gate"],
            "decision": report["falsification_gate"]["status"],
            "timestamp": now(),
            "reproducibility_artifact": RAW_RESULT,
            "independent_validation": VALIDATION,
            "exit_code": 0,
        })
    events_path = ROOT / "research/supervisor_events.jsonl"
    existing_events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not any(row.get("event") == "local_experiment_scientifically_reconciled" and row.get("experiment_id") == EXPERIMENT_ID for row in existing_events):
        append_jsonl(events_path, {
            "event": "local_experiment_scientifically_reconciled",
            "task_id": TASK_ID,
            "experiment_id": EXPERIMENT_ID,
            "scientific_success": True,
            "falsification_status": report["falsification_gate"]["status"],
            "matching_ratio_failure": False,
            "invariant_failure": True,
            "timestamp": now(),
        })
    supervisor = read_json(ROOT / "research/supervisor_state.json")
    sync_track_checkpoints(ROOT, state, queue, supervisor)
    print(json.dumps({"completed": TASK_ID, "round": state["current_research_round"],
                      "experiments_started": state["budget_consumption"]["experiments_started"],
                      "next_action": state["next_action"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
