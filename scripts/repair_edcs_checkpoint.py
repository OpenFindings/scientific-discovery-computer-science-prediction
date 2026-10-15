#!/usr/bin/env python3
"""Repair a supervisor misclassification without rerunning the experiment.

The first scientific reconciliation correctly recorded the EDCS result, but a
later supervisor pass read the compact raw result as the task artifact and
classified it as artifact_only. This repair is idempotent, does not alter
lifetime experiment counters, and preserves the historical false event.
"""
from __future__ import annotations

import json
from pathlib import Path

from research_supervisor import append_jsonl, atomic_json, now, read_json, sync_track_checkpoints

ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "NOVEL-EDCS-LAZY-REPAIR-EXPERIMENT-001"
REPORT = "reports/edcs_experiment_result_20261015.json"
RAW = "results/edcs_lazy_repair_counterexample_20261015/result.json"
VALIDATION = "results/edcs_lazy_repair_counterexample_20261015/independent_validation.json"
EVENT = "artifact_only_misclassification_repaired"


def repair_task(task: dict, report: dict) -> None:
    task["artifact"] = REPORT
    task["status"] = "completed"
    task["scientific_status"] = "scientifically_completed"
    task["scientific_validation"] = {
        "mode": "experiment_result",
        "scientific_success": True,
        "missing_or_failed": [],
        "reason": "structured scientific report and independent validation satisfy the experiment gate",
    }
    last = task.setdefault("last_result", {})
    last.update({
        "artifact_valid": True,
        "scientific_success": True,
        "scientific_report": REPORT,
        "raw_result": RAW,
        "independent_validation": VALIDATION,
        "falsification_status": report["falsification_gate"]["status"],
    })


def main() -> int:
    report = read_json(ROOT / REPORT)
    queue_paths = [ROOT / "research/task_queue.json", ROOT / "research/tracks/experiments/task_queue.json"]
    queues = [read_json(path) for path in queue_paths]
    matched = 0
    for queue in queues:
        for task in queue.get("tasks", []):
            if task.get("task_id") == TASK_ID:
                repair_task(task, report)
                matched += 1
    if matched != 2:
        raise SystemExit(f"expected task in both queues, found {matched}")

    state = read_json(ROOT / "research/state.json")
    state.setdefault("completed_tasks", [])
    if TASK_ID not in state["completed_tasks"]:
        state["completed_tasks"].append(TASK_ID)
    state["artifact_only_tasks"] = [x for x in state.get("artifact_only_tasks", []) if x != TASK_ID]
    state["pending_tasks"] = [task["task_id"] for task in queues[0]["tasks"] if task.get("status") in {"pending", "failed"}]
    state["campaign_status"] = "waiting_for_eligible_task"
    state["idle_reason"] = "single_authorized_edcs_experiment_consumed_no_further_experiment_execution"
    state["next_action"] = "Stop experimental execution for this authorization cycle; preserve the EDCS mathematical generalization and Paper 3 no-score state. Any revised repair rule requires a new protocol and explicit authorization."
    state["current_best_opportunities"] = [
        {
            "id": "EDCS-LAZY-REPAIR-INVARIANT-001",
            "status": "variant_falsified_mathematical_generalization_pending_authorization",
            "reason": "one-flip variant has a proved parameterized failure family for beta_minus=beta-1; original EDCS remains untested",
        },
        {
            "id": "PAPER3-TARGET-B-EVIDENCE-GROWTH",
            "status": "frozen_no_score_until_labels",
            "reason": "Target B protocol is frozen, but no valid historical forecast labels are available",
        },
    ]
    state["opportunity_ranking"] = [
        {
            "rank": 1,
            "id": "EDCS-LAZY-REPAIR-INVARIANT-001",
            "status": "mathematical_generalization_pending_authorization",
            "basis": "proved failure family for the stated one-toggle model; no new execution authorized",
            "score": None,
        },
        {
            "rank": 2,
            "id": "PAPER3-TARGET-B-EVIDENCE-GROWTH",
            "status": "frozen_no_score_until_labels",
            "basis": "protocol frozen; direct historical outcomes remain unavailable",
            "score": None,
        },
    ]
    state["latest_scientific_increment"] = {
        "kind": "mathematical_generalization_of_finite_variant_counterexample",
        "task_id": TASK_ID,
        "scientific_success": True,
        "evidence_level": "tier_4_independently_reproduced_finite_counterexample_plus_proved_variant_family",
        "decision": "one_flip_local_repair_impossibility_for_stated_class",
        "observed_result": "The four-edge witness extends to every integer beta>=3 with beta_minus=beta-1; a P2-required insertion and a newly created P1 violation require at least two single-edge H toggles.",
        "next_falsifiable_action": state["next_action"],
    }
    audits = state.setdefault("scientific_artifact_audits", [])
    audits[:] = [row for row in audits if row.get("artifact") not in {
        "reports/edcs_mathematical_research_note_20261015.md",
        "reports/edcs_provenance_audit_20261015.json",
    }]
    audits.append({
        "artifact": "reports/edcs_mathematical_research_note_20261015.md",
        "task_id": TASK_ID,
        "evidence_level": "tier_4_independently_reproduced_finite_counterexample_plus_proved_variant_family",
        "scientific_success": True,
        "scientific_validation": {
            "mode": "mathematical_generalization",
            "scientific_success": True,
            "missing_or_failed": [],
            "reason": "fixed witness replay and parameterized proof obligations recorded; no original-EDCS novelty claim",
        },
        "observed_result_or_blocker": "For beta=b>=3 and beta_minus=b-1, the star-plus-cross-edge family requires at least two single-edge H toggles after the cross insertion.",
        "uncertainty": [
            "The proof is for the explicitly stated one-toggle repair class and does not cover compound swaps.",
            "It does not refute Bernstein-Stein EDCS theory or algorithm.",
            "Publication-level novelty is unverified."
        ],
        "next_falsifiable_action": state["next_action"],
        "timestamp": now(),
    })
    audits.append({
        "artifact": "reports/edcs_provenance_audit_20261015.json",
        "task_id": TASK_ID,
        "evidence_level": "tier_3_provenance_audit",
        "scientific_success": True,
        "scientific_validation": {
            "mode": "provenance_audit",
            "scientific_success": True,
            "missing_or_failed": ["strict_temporal_preregistration_timestamp"],
            "reason": "Git commit chronology supports content-before-execution, but declared frozen_at is inconsistent",
        },
        "observed_result_or_blocker": "Protocol commit d54db55 precedes observed result/validation files, while frozen_at=06:15Z follows them.",
        "uncertainty": ["Filesystem mtimes are non-authoritative; runner stores only monotonic start time."],
        "next_falsifiable_action": state["next_action"],
        "timestamp": now(),
    })
    state["checkpoint_time"] = now()
    # Do not increment experiments_started, completed_experiments, or rounds:
    # this is a state repair, not a new run.
    for queue, path in zip(queues, queue_paths):
        atomic_json(path, queue)
    atomic_json(ROOT / "research/state.json", state)

    events_path = ROOT / "research/supervisor_events.jsonl"
    rows = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not any(row.get("event") == EVENT and row.get("task_id") == TASK_ID for row in rows):
        append_jsonl(events_path, {
            "event": EVENT,
            "task_id": TASK_ID,
            "timestamp": now(),
            "scientific_success": True,
            "cause": "supervisor read compact raw result instead of structured scientific report",
            "historical_false_classification_preserved": True,
            "lifetime_experiment_counter_changed": False,
        })
    supervisor = read_json(ROOT / "research/supervisor_state.json")
    sync_track_checkpoints(ROOT, state, queues[0], supervisor)
    print(json.dumps({"repaired": TASK_ID, "matched_queues": matched, "counters_changed": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
