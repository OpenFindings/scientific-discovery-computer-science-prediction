#!/usr/bin/env python3
"""Independently reconcile a valid Paper 3 diagnosis after worker path rejection."""
from __future__ import annotations

import json
from pathlib import Path

from research_supervisor import append_jsonl, atomic_json, now, read_json, scientific_validation, sync_track_checkpoints


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "PAPER3-OBSERVABILITY-CAUSE-DIAGNOSIS-001"


def main() -> int:
    state = read_json(ROOT / "research/state.json")
    queue = read_json(ROOT / "research/task_queue.json")
    task = next(row for row in queue["tasks"] if row["task_id"] == TASK_ID)
    artifact = read_json(ROOT / task["artifact"])
    ok, validation = scientific_validation(task, artifact)
    if not ok:
        raise SystemExit(json.dumps(validation, ensure_ascii=False))
    task["status"] = "completed"
    task["scientific_status"] = "scientifically_completed_after_independent_reconciliation"
    task["scientific_validation"] = validation
    task.setdefault("last_result", {})["scientific_success"] = True
    task["last_result"]["scientific_validation_reconciled"] = True
    task["last_result"]["worker_integrity_failure"] = "worker changed paths outside declared artifact: research/state.json"
    task["worker_status"] = "write_conflict_rejected"
    task["worker_failure_note"] = "artifact retained; supervisor-owned state write rejected and diagnosis independently reconciled"
    if TASK_ID not in state.setdefault("completed_tasks", []):
        state["completed_tasks"].append(TASK_ID)
        state["current_research_round"] = int(state.get("current_research_round", 0)) + 1
    state["blocked_tasks"] = [x for x in state.get("blocked_tasks", []) if x != TASK_ID]
    state["artifact_only_tasks"] = [x for x in state.get("artifact_only_tasks", []) if x != TASK_ID]
    state["pending_tasks"] = [x["task_id"] for x in queue["tasks"] if x.get("status") in {"pending", "failed"}]
    state["campaign_status"] = "waiting_for_next_activation"
    state["current_phase"] = TASK_ID.lower()
    state["next_action"] = artifact["next_falsifiable_action"]
    state["latest_scientific_increment"] = {
        "kind": "paper3_cross_round_observability_diagnosis",
        "task_id": TASK_ID,
        "scientific_success": True,
        "evidence_level": artifact["evidence_tier"],
        "decision": artifact["observed_result_or_blocker"]["diagnosis"],
        "direct_label_yield": artifact["cross_round_counts"]["unique_direct_label_yield"],
        "independent_validation": task["artifact"],
        "next_falsifiable_action": artifact["next_falsifiable_action"],
    }
    state.setdefault("actual_experiment_results", []).append({
        "artifact": task["artifact"],
        "evidence_level": artifact["evidence_tier"],
        "experiment_id": "AUDIT-PAPER3-OBSERVABILITY-CAUSE-DIAGNOSIS-001",
        "limitation": "; ".join(artifact["uncertainty"]),
        "result": artifact["observed_result_or_blocker"]["diagnosis"],
    })
    state["worker_integrity_failures"] = [row for row in state.get("worker_integrity_failures", []) if row.get("task_id") != TASK_ID]
    state["worker_integrity_failures"].append({
        "task_id": TASK_ID,
        "attempt": task.get("attempts", 1),
        "path": "research/state.json",
        "interpretation": "artifact retained, worker execution rejected, diagnosis independently reconciled",
        "timestamp": now(),
    })
    state["checkpoint_time"] = now()
    atomic_json(ROOT / "research/task_queue.json", queue)
    atomic_json(ROOT / "research/state.json", state)
    append_jsonl(ROOT / "research/supervisor_events.jsonl", {
        "event": "paper3_diagnosis_independently_reconciled_after_worker_conflict",
        "task_id": TASK_ID,
        "scientific_success": True,
        "direct_label_yield": artifact["cross_round_counts"]["unique_direct_label_yield"],
        "timestamp": now(),
    })
    supervisor = read_json(ROOT / "research/supervisor_state.json")
    sync_track_checkpoints(ROOT, state, queue, supervisor)
    print(json.dumps({"task_id": TASK_ID, "scientific_success": True, "direct_label_yield": artifact["cross_round_counts"]["unique_direct_label_yield"], "round": state["current_research_round"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
