#!/usr/bin/env python3
"""Reconcile the novel-CS discovery planning cycle without starting an experiment.

This checkpoint records scientific planning/audit decisions separately from
execution.  The EDCS experiment remains blocked until an explicit local
experiment authorization is added; this script never changes lifetime
experiment counters or silently renews that authorization.
"""
from __future__ import annotations

import json
from pathlib import Path

from research_supervisor import append_jsonl, atomic_json, now, read_json, sync_track_checkpoints

ROOT = Path(__file__).resolve().parents[1]

COMPLETED = [
    {
        "task_id": "PAPER3-TARGET-B-PROTOCOL-FREEZE-001",
        "research_key": "paper3_target_b_evidence_growth_protocol",
        "track": "forecasting",
        "objective": "Freeze a separate Paper 3 Target B protocol for independently verifiable scientific progress while preserving the original direct-resolution cohorts and labels.",
        "artifact": "research/paper3_target_b_protocol_v1.json",
        "priority": 93,
        "expected_information_gain": 0.82,
        "cost_estimate": 0.15,
        "dependencies": [],
        "success_criteria": [
            "Target A and Target B remain separate",
            "source-only chronological features and leakage rules are explicit",
            "minimum label gates and no-score rule are frozen",
            "original cohorts are explicitly immutable",
        ],
        "failure_handling": "Do not score Paper 3 until the frozen label and temporal-split gates are met.",
        "status": "completed",
        "attempts": 0,
        "max_attempts": 1,
        "scientific_status": "scientifically_completed",
        "scientific_validation": {
            "mode": "protocol_freeze",
            "scientific_success": True,
            "reason": "Target B protocol is frozen with explicit label gates and no-score conditions",
            "missing_or_failed": [],
        },
    },
    {
        "task_id": "NOVEL-CS-OPPORTUNITY-SOURCE-AUDIT-001",
        "research_key": "novel_cs_candidate_source_audit",
        "track": "experiments",
        "objective": "Audit fresh CS candidates outside the exhausted QAOA, Badger, CAM, SERENIoT and DP158 directions, and reject candidates lacking a source-level novelty boundary or executable objective endpoint.",
        "artifact": "reports/novel_cs_opportunity_pool_20261015.json",
        "priority": 94,
        "expected_information_gain": 0.86,
        "cost_estimate": 0.25,
        "dependencies": [],
        "success_criteria": [
            "at least three fresh candidate questions source-audited",
            "objective endpoint and feasibility gate recorded for each",
            "known prior art and unresolved boundary separated",
            "one candidate selected without hindsight from later outcomes",
        ],
        "failure_handling": "A bounded source audit is a valid rejection when the endpoint, dependency or novelty gate fails; do not promote a literature lead to a discovery.",
        "status": "completed",
        "attempts": 0,
        "max_attempts": 1,
        "scientific_status": "scientifically_completed",
        "scientific_validation": {
            "mode": "source_level_opportunity_audit",
            "scientific_success": True,
            "reason": "Four candidates were bounded; two were rejected and EDCS was selected conditionally",
            "missing_or_failed": [],
        },
    },
    {
        "task_id": "PAPER4-NOVEL-ACTION-PLAN-FREEZE-001",
        "research_key": "paper4_novel_action_comparison",
        "track": "experiments",
        "objective": "Freeze a Paper 4 comparison across genuinely feasible research actions, declare score assumptions and baselines, and execute no action until the local experiment authorization gate is satisfied.",
        "artifact": "reports/paper4_novel_action_plan_20261015.json",
        "priority": 92,
        "expected_information_gain": 0.78,
        "cost_estimate": 0.18,
        "dependencies": ["NOVEL-CS-OPPORTUNITY-SOURCE-AUDIT-001"],
        "success_criteria": [
            "at least three candidate actions or an explicit feasibility rejection",
            "cost and information-gain assumptions are declared",
            "simple ranking baselines are recorded",
            "planner superiority is not claimed from assumed scores",
        ],
        "failure_handling": "Planning scores remain assumptions until observed evidence change is measured; infeasible actions are not treated as scientific failures.",
        "status": "completed",
        "attempts": 0,
        "max_attempts": 1,
        "scientific_status": "scientifically_completed",
        "scientific_validation": {
            "mode": "planning_protocol",
            "scientific_success": True,
            "reason": "Three actions were compared; EDCS was selected only conditionally and remains unexecuted",
            "missing_or_failed": [],
        },
    },
    {
        "task_id": "PAPER4-QAOA-CLOSURE-001",
        "research_key": "paper4_qaoa_direction_closure",
        "track": "experiments",
        "objective": "Close the authorized QAOA investigation with separate conditional state-quality, complete-procedure, shot-budget and novelty conclusions.",
        "artifact": "reports/qaoa_closure_conclusion_20261015.json",
        "priority": 91,
        "expected_information_gain": 0.76,
        "cost_estimate": 0.12,
        "dependencies": ["PAPER4-QAOA-FAIR-SHOT-COST-001"],
        "success_criteria": [
            "independent conditional replication retained",
            "negative fair-cost result retained",
            "graph-family and simulation limitations stated",
            "no quantum advantage or novelty claim made",
        ],
        "failure_handling": "Do not repeat QAOA parameter sweeps without a substantively new hypothesis and explicit renewed budget.",
        "status": "completed",
        "attempts": 0,
        "max_attempts": 1,
        "scientific_status": "scientifically_completed",
        "scientific_validation": {
            "mode": "negative_result_closure",
            "scientific_success": True,
            "reason": "The conditional effect and negative complete-procedure cost result are separately documented",
            "missing_or_failed": [],
        },
    },
]

BLOCKED = {
    "task_id": "NOVEL-EDCS-LAZY-REPAIR-EXPERIMENT-001",
    "research_key": "edcs_lazy_repair_invariant_counterexample",
    "track": "experiments",
    "objective": "Test whether the frozen lazy edge-deletion/local-repair implementation preserves the EDCS endpoint inequalities and matching-quality guarantee on bounded simple graphs and deletion sequences.",
    "artifact": "results/edcs_lazy_repair_counterexample_20261015/result.json",
    "priority": 99,
    "expected_information_gain": 0.80,
    "cost_estimate": 0.30,
    "dependencies": ["NOVEL-CS-OPPORTUNITY-SOURCE-AUDIT-001", "PAPER4-NOVEL-ACTION-PLAN-FREEZE-001"],
    "success_criteria": [
        "exact enumeration or bounded deletion search completes under the declared limit",
        "all candidate traces and implementation parameters are retained",
        "any counterexample is minimized and independently recomputed",
        "survival is reported only as finite evidence, never as a proof",
    ],
    "failure_handling": "A finite search that finds no counterexample narrows the question but does not prove the invariant; implementation or runtime failure is recorded separately.",
    "execution_requirements": [
        "explicit renewed local experiment authorization",
        "Python 3.12 and existing standard-library tooling only",
        "one process, no network, <=120 CPU seconds, <=1024 MiB",
        "n<=6 exact enumeration plus deletion sequences of length <=6; bounded n<=8 extension only if the first gate passes",
    ],
    "counts_as_experiment": True,
    "status": "blocked",
    "attempts": 0,
    "max_attempts": 1,
    "scientific_status": "blocked_pending_explicit_authorization",
    "failure_note": "blocked_pending_explicit_experiment_authorization",
    "scientific_validation": {
        "mode": "authorization_gate",
        "scientific_success": False,
        "reason": "The candidate is frozen but cannot execute after the configured lifetime experiment authorization was exhausted",
        "missing_or_failed": ["explicit_local_experiment_authorization"],
    },
}


def main() -> int:
    required_artifacts = [*(task["artifact"] for task in COMPLETED), BLOCKED["artifact"]]
    for relative in required_artifacts[:-1]:
        if not (ROOT / relative).is_file():
            raise SystemExit(f"missing checkpoint artifact: {relative}")

    state = read_json(ROOT / "research/state.json")
    queue = read_json(ROOT / "research/task_queue.json")
    tasks = queue.setdefault("tasks", [])
    by_id = {task.get("task_id"): task for task in tasks}
    newly_completed = []
    for task in COMPLETED:
        existing = by_id.get(task["task_id"])
        if existing is None:
            tasks.append(dict(task))
            newly_completed.append(task["task_id"])
        else:
            # Do not overwrite execution history if this script is rerun.
            existing.update({key: value for key, value in task.items() if key not in {"attempts", "started_at", "finished_at", "last_result"}})

    existing_blocked = by_id.get(BLOCKED["task_id"])
    if existing_blocked is None:
        tasks.append(dict(BLOCKED))
    else:
        existing_blocked.update({key: value for key, value in BLOCKED.items() if key not in {"attempts", "started_at", "finished_at", "last_result"}})

    state.setdefault("completed_tasks", [])
    for task_id in (task["task_id"] for task in COMPLETED):
        if task_id not in state["completed_tasks"]:
            state["completed_tasks"].append(task_id)
            state["current_research_round"] = int(state.get("current_research_round", 0)) + 1
    state["pending_tasks"] = [task["task_id"] for task in tasks if task.get("status") in {"pending", "failed"}]
    state["blocked_tasks"] = [task["task_id"] for task in tasks if task.get("status") == "blocked"]
    state["current_phase"] = BLOCKED["task_id"].lower()
    state["campaign_status"] = "waiting_for_experiment_authorization"
    state["idle_reason"] = "selected_novel_experiment_blocked_pending_explicit_authorization"
    state["next_action"] = "Obtain explicit authorization for exactly one EDCS bounded experiment (<=120 CPU seconds, <=1024 MiB, one process, no network); do not reset the lifetime experiment counter."
    state["opportunity_ranking"] = [
        {
            "task_id": BLOCKED["task_id"],
            "track": "experiments",
            "status": "blocked_pending_explicit_authorization",
            "score": round(BLOCKED["priority"] * BLOCKED["expected_information_gain"] / BLOCKED["cost_estimate"], 4),
            "scientific_completion": "authorization_gate",
        },
        {
            "task_id": "PAPER3-TARGET-B-PROTOCOL-FREEZE-001",
            "track": "forecasting",
            "status": "protocol_frozen_no_score_until_labels",
            "score": None,
        },
    ]
    state["latest_scientific_increment"] = {
        "kind": "novel_cs_source_audit_and_protocol_freeze",
        "task_id": BLOCKED["task_id"],
        "scientific_success": False,
        "evidence_level": "tier_2_source_audited_hypothesis_waiting_authorization",
        "decision": "EDCS selected conditionally; no experiment executed",
        "next_falsifiable_action": state["next_action"],
    }
    state["checkpoint_time"] = now()

    atomic_json(ROOT / "research/task_queue.json", queue)
    atomic_json(ROOT / "research/state.json", state)
    supervisor = read_json(ROOT / "research/supervisor_state.json")
    sync_track_checkpoints(ROOT, state, queue, supervisor)

    for task_id in newly_completed:
        append_jsonl(ROOT / "research/supervisor_events.jsonl", {
            "event": "scientifically_justified_planning_checkpoint_reconciled",
            "task_id": task_id,
            "scientific_success": True,
            "timestamp": now(),
        })
    if not existing_blocked:
        append_jsonl(ROOT / "research/supervisor_events.jsonl", {
            "event": "novel_experiment_blocked_pending_explicit_authorization",
            "task_id": BLOCKED["task_id"],
            "counts_as_experiment": True,
            "lifetime_experiment_counter_changed": False,
            "authorization_request": {"cpu_seconds": 120, "memory_mib": 1024, "network": False, "processes": 1},
            "timestamp": now(),
        })
    print(json.dumps({
        "newly_completed": newly_completed,
        "blocked_task": BLOCKED["task_id"],
        "pending": state["pending_tasks"],
        "experiment_authorization_changed": False,
        "round": state["current_research_round"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
