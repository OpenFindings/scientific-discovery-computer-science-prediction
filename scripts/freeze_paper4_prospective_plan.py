#!/usr/bin/env python3
"""Freeze the Paper 4 prospective action plan before observing new outcomes."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def build_plan() -> dict:
    return {
        "plan_id": "PAPER4-PROSPECTIVE-2026-10-15-v1",
        "status": "FROZEN_BEFORE_EXECUTION",
        "evidence_boundary": "Planning assumptions are not observations; no candidate was selected using a new experimental outcome.",
        "prior_sources": [
            "reports/historical_observable_cohort_round3.json",
            "reports/paper4_action_outcome_audit.json",
            "https://arxiv.org/html/2011.05425v1"
        ],
        "candidates": [
            {
                "id": "A1",
                "name": "QAOA source-baseline reproduction",
                "scientific_hypothesis": "On small random 3-regular graphs, source-style 2-independent-set postselection changes the depth-1 QAOA MaxCut satisfied-edge fraction relative to unconditioned depth-1 QAOA.",
                "competing_explanation": "Any apparent gain is caused by graph-size, parameter, conditioning-probability or postprocessing differences rather than postselection.",
                "prior_work": ["2011.05425v1 Sections 2, 5 and 7"],
                "required_inputs": ["pure Python/Numpy state-vector simulator", "deterministic random 3-regular graph generator", "source parameter convention"],
                "implementation_effort_hours": 2,
                "feasibility_assumption": {"value": 0.9, "justification": "The machine has Python 3.12 and NumPy; n<=10 exact state vectors need no external dataset or quantum runtime."},
                "expected_information_gain_model": {"prior_H1": 0.5, "conditional_sensitivity": 0.8, "conditional_specificity": 0.8, "conditional_gain_bits": 0.278072, "feasibility_discounted_bits": 0.250265, "assumption_note": "Illustrative binary entropy model, not calibrated probability."},
                "measurable_outcome": "Mean and per-graph satisfied-edge fraction, conditioning probability and simulator cost over fixed seeds.",
                "falsification_condition": "Reject the source-style effect if the paired mean difference is non-positive or disappears when graph, parameter and conditioning costs are matched.",
                "baseline_selection_score": {"paper4_assumption_score": 0.82, "lowest_cost_score": 0.95, "random_selection_score": 0.5},
                "experiment_budget": {"max_graphs": 20, "vertices": 8, "max_wall_seconds": 120, "seed": 20261015}
            },
            {
                "id": "A2",
                "name": "Alternative 3-independent-set postselection",
                "scientific_hypothesis": "A 3-independent-set conditioning configuration can improve the satisfied-edge fraction beyond the unconditioned baseline at matched state-vector and conditioning accounting.",
                "competing_explanation": "The alternative conditioning set is too rare or its gain is a finite-size artifact; source-style 2-independent conditioning may remain better.",
                "prior_work": ["2011.05425v1 Sections 4.2, 5.1 and 7"],
                "required_inputs": ["A1 simulator", "deterministic 3-independent-set enumerator", "same graph/parameter seeds"],
                "implementation_effort_hours": 4,
                "feasibility_assumption": {"value": 0.75, "justification": "Enumeration is feasible for n=8, but the alternative projection is not source-validated and must remain a pilot."},
                "expected_information_gain_model": {"prior_H1": 0.5, "conditional_sensitivity": 0.7, "conditional_specificity": 0.8, "conditional_gain_bits": 0.236452, "feasibility_discounted_bits": 0.177339, "assumption_note": "Illustrative scenario only."},
                "measurable_outcome": "Paired difference versus A1 and unconditioned baseline, including conditioning probability and wall-clock cost.",
                "falsification_condition": "Reject if no positive paired difference remains at fixed graph family and cost accounting, or if the effect is present only on one seed.",
                "baseline_selection_score": {"paper4_assumption_score": 0.64, "lowest_cost_score": 0.55, "random_selection_score": 0.5},
                "experiment_budget": {"max_graphs": 20, "vertices": 8, "max_wall_seconds": 180, "seed": 20261015}
            },
            {
                "id": "A3",
                "name": "Small exact complexity-question search",
                "scientific_hypothesis": "A bounded exhaustive search over small coupled-task tree instances can find a counterexample to a simple greedy schedule, informing but not resolving the source's open complexity question.",
                "competing_explanation": "The chosen instance bound is too small to expose a counterexample; a null search is not evidence of a theorem.",
                "prior_work": ["reports/historical_observable_source_screen_round3.json"],
                "required_inputs": ["source-defined instance model", "exact small-instance enumerator", "greedy baseline"],
                "implementation_effort_hours": 5,
                "feasibility_assumption": {"value": 0.6, "justification": "The source question is formal but its complete objective/compatibility definition must be reconstructed before coding."},
                "expected_information_gain_model": {"prior_H1": 0.5, "conditional_sensitivity": 0.6, "conditional_specificity": 0.8, "conditional_gain_bits": 0.152003, "feasibility_discounted_bits": 0.091202, "assumption_note": "Illustrative scenario only."},
                "measurable_outcome": "Exact optimum minus greedy schedule on each enumerated instance and reproducible counterexample witness if found.",
                "falsification_condition": "Reject the action as not yet well-defined if the source objective cannot be reconstructed without inventing assumptions.",
                "baseline_selection_score": {"paper4_assumption_score": 0.31, "lowest_cost_score": 0.35, "random_selection_score": 0.5},
                "experiment_budget": {"max_instances": 5000, "max_wall_seconds": 180, "seed": 20261015}
            }
        ],
        "selection_rule": "Select the highest feasibility-gated information-per-cost action; use lowest-cost and random-selection scores as descriptive baselines. Do not update scores after outcomes.",
        "selected_action": "A2",
        "selected_action_reason": "A2 directly tests the unresolved source-grounded postselection extension, is locally executable after the A1 simulator core, and has higher expected information per hour than A3 under the frozen assumptions. A1 baseline measurements are required inside the same preregistered run.",
        "outcome_comparison": ["Paper4 frozen rank", "lowest-cost A1 baseline", "uniform random candidate order"],
        "global_falsification_gate": "If no candidate has pinned inputs and objective endpoints, stop without a utility claim; any null or setup failure is retained as evidence and does not become a breakthrough."
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("reports/paper4_prospective_plan_v1.json"))
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite frozen plan: {args.output}")
    plan = build_plan()
    plan["frozen_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    canonical = json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    plan["plan_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "plan_id": plan["plan_id"], "plan_sha256": plan["plan_sha256"], "selected_action": plan["selected_action"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
