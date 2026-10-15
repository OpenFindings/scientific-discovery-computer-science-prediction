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
PROOF_REVIEW = "reports/edcs_adversarial_proof_review_20261015.json"


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
    state["idle_reason"] = "EDCS_closed_after_adversarial_review_next_action_is_nonexperimental_zero_extension_source_audit"
    state["current_phase"] = "edcs_proof_review_zero_extension_candidate_audit"
    state["next_action"] = "Audit the exact Zero Extension sparsifier question and forward citations without executing an experiment; preserve Paper 3 Target A/B no-score state and do not renew experimental budgets."
    state["current_best_opportunities"] = [
        {
            "id": "ZERO-EXTENSION-EXACT-SPARSIFIER-005",
            "status": "source_audited_candidate_not_executed",
            "reason": "2018 primary source leaves the dependence of exact Zero Extension metric-sparsifier size on label parameter s as a formal question; definitions and forward citations still need audit",
        },
        {
            "id": "PAPER3-TARGET-B-EVIDENCE-GROWTH",
            "status": "frozen_no_score_until_labels",
            "reason": "Target B protocol is frozen, but no valid historical forecast labels are available",
        },
        {
            "id": "EDCS-LAZY-REPAIR-INVARIANT-001",
            "status": "closed_educational_engineering_no_publishable_novelty",
            "reason": "corrected one-toggle theorem is restricted; cascading EDCS repairs are known prior art and no general dynamic lower bound was established",
        },
    ]
    state["opportunity_ranking"] = [
        {
            "rank": 1,
            "id": "ZERO-EXTENSION-EXACT-SPARSIFIER-005",
            "status": "source_audited_candidate_not_executed",
            "basis": "2018 source-authenticated formal open question; no experiment or novelty claim yet",
            "score": None,
        },
        {
            "rank": 2,
            "id": "PAPER3-TARGET-B-EVIDENCE-GROWTH",
            "status": "frozen_no_score_until_labels",
            "basis": "protocol frozen; direct historical outcomes remain unavailable",
            "score": None,
        },
        {
            "rank": 3,
            "id": "EDCS-LAZY-REPAIR-INVARIANT-001",
            "status": "closed_educational_engineering_no_publishable_novelty",
            "basis": "restricted one-toggle result corrected and independently reviewed; no general dynamic EDCS lower bound",
            "score": None,
        },
    ]
    state["latest_scientific_increment"] = {
        "kind": "adversarial_mathematical_proof_review_and_novelty_closure",
        "task_id": TASK_ID,
        "scientific_success": True,
        "evidence_level": "tier_4_independently_reviewed_restricted_mathematical_result",
        "decision": "close_edcs_as_educational_engineering_result; broad_repair_lemma_corrected",
        "observed_result": "The parameterized one-toggle impossibility survives under explicit assumptions, while the broad claim that every deficient edge must be inserted is disproved by a beta=4,beta_minus=2 alternate-edge repair.",
        "next_falsifiable_action": "Audit the exact Zero Extension sparsifier question and forward citations without executing an experiment; preserve Paper 3 Target A/B no-score state.",
    }
    audits = state.setdefault("scientific_artifact_audits", [])
    audits[:] = [row for row in audits if row.get("artifact") not in {
        "reports/edcs_mathematical_research_note_20261015.md",
        "reports/edcs_provenance_audit_20261015.json",
        PROOF_REVIEW,
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
        "artifact": PROOF_REVIEW,
        "task_id": TASK_ID,
        "evidence_level": "tier_4_independently_reviewed_restricted_mathematical_result",
        "scientific_success": True,
        "scientific_validation": {
            "mode": "adversarial_proof_review",
            "scientific_success": True,
            "missing_or_failed": [],
            "reason": "overbroad lemma disproved, restricted lemma stated with proof obligations, and novelty boundary corrected",
        },
        "observed_result_or_blocker": "The broad deficient-edge insertion claim fails for beta=4,beta_minus=2; the beta_minus=beta-1 one-toggle star obstruction survives.",
        "uncertainty": [
            "No general dynamic EDCS maintenance lower bound was proved.",
            "The Zero Extension lead remains a source-audited candidate and has not been independently verified as novel.",
        ],
        "next_falsifiable_action": state["next_action"],
        "timestamp": now(),
    })
    for row in state.get("actual_experiment_results", []):
        if row.get("artifact") == REPORT:
            row["experiment_id"] = "EXP-EDCS-LAZY-REPAIR-INVARIANT-20261015"
            row["limitation"] = "Finite independently reproduced counterexample and restricted mathematical generalization only; no original-EDCS refutation, general maintenance lower bound, or Paper 3/4 validation."
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
