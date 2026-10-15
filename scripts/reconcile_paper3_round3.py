#!/usr/bin/env python3
"""Supervisor-owned reconciliation after independent Paper 3 artifact validation."""
from __future__ import annotations

import json
from pathlib import Path

from research_supervisor import (
    EVENTS,
    QUEUE,
    STATE,
    SUPERVISOR_STATE,
    append_jsonl,
    atomic_json,
    load_supervisor_state,
    now,
    read_json,
    scientific_validation,
    sync_track_checkpoints,
    update_scientific_checkpoint,
    write_supervisor_state,
)

ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "PAPER3-OBSERVABILITY-ROUND3-001"


def main() -> int:
    validation_report = read_json(ROOT / "reports/paper3_round3_independent_validation.json")
    if not validation_report.get("all_checks_passed"):
        raise SystemExit("independent validation did not pass")
    state = read_json(ROOT / STATE)
    queue = read_json(ROOT / QUEUE)
    task = next(task for task in queue["tasks"] if task["task_id"] == TASK_ID)
    artifact = read_json(ROOT / task["artifact"])
    scientific_ok, scientific = scientific_validation(task, artifact)
    if not scientific_ok:
        raise SystemExit(json.dumps(scientific))

    task["status"] = "completed"
    task["worker_status"] = "write_conflict_rejected"
    task["scientific_status"] = "scientifically_completed_after_independent_reconciliation"
    task["scientific_validation"] = {
        **scientific,
        "independent_validation": str((ROOT / "reports/paper3_round3_independent_validation.json").relative_to(ROOT)),
        "execution_integrity": "worker artifact accepted only after supervisor rejected its research/state.json write and independently revalidated the artifact",
    }
    task["worker_failure_note"] = task.pop("failure_note", "worker changed a supervisor-owned path")
    task["last_result"]["scientific_success"] = False
    task["last_result"]["scientific_validation_reconciled"] = True
    blocked = state.setdefault("blocked_tasks", [])
    if TASK_ID in blocked:
        blocked.remove(TASK_ID)
    completed = state.setdefault("completed_tasks", [])
    if TASK_ID not in completed:
        completed.append(TASK_ID)
        state["current_research_round"] = state.get("current_research_round", 0) + 1
    conflicts = state.setdefault("worker_integrity_failures", [])
    if TASK_ID not in [row.get("task_id") for row in conflicts]:
        conflicts.append({
            "task_id": TASK_ID,
            "attempt": task.get("attempts"),
            "path": "research/state.json",
            "interpretation": "artifact retained, worker execution rejected, scientific objective independently reconciled",
            "timestamp": now(),
        })
    state["campaign_status"] = "waiting_for_next_activation"
    state["current_phase"] = TASK_ID.lower()
    state["checkpoint_time"] = now()

    atomic_json(ROOT / QUEUE, queue)
    update_scientific_checkpoint(ROOT, state, task, artifact, True, task["scientific_validation"])
    state["next_action"] = artifact["next_falsifiable_action"]
    state["pending_tasks"] = [row["task_id"] for row in queue["tasks"] if row.get("status") in {"pending", "failed"}]
    atomic_json(ROOT / STATE, state)
    append_jsonl(ROOT / EVENTS, {
        "event": "scientific_artifact_independently_reconciled_after_worker_conflict",
        "task_id": TASK_ID,
        "timestamp": now(),
        "worker_path_conflict": "research/state.json",
        "scientific_success": True,
        "paper3_gate": artifact["paper3_gate"]["status"],
        "direct_label_yield": artifact["observed_result"]["direct_label_yield"],
    })
    supervisor = load_supervisor_state(ROOT, state.get("campaign_id", "research"))
    supervisor["status"] = "ACTIVE"
    supervisor["last_event"] = {"event": "scientific_artifact_independently_reconciled_after_worker_conflict", "task_id": TASK_ID, "timestamp": now()}
    write_supervisor_state(ROOT, supervisor)
    sync_track_checkpoints(ROOT, state, queue, supervisor)
    print(json.dumps({"task_id": TASK_ID, "status": task["status"], "scientific_status": task["scientific_status"], "paper3_gate": artifact["paper3_gate"]["status"], "direct_label_yield": artifact["observed_result"]["direct_label_yield"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
