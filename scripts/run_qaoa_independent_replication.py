#!/usr/bin/env python3
"""Run the predeclared second n=10 QAOA A1 replication."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.run_qaoa_postselection_pilot import (  # noqa: E402
    conditioned_expectation,
    greedy_k_independent,
    qaoa_state,
    simple_3_regular,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/qaoa_source_baseline_replication_20261015/result.json"))
    args = parser.parse_args()
    n, graph_count, seed = 10, 20, 20261016
    beta, gamma = -math.pi / 4, math.pi / 4
    original = ROOT / "results/qaoa_source_baseline_larger_n_20261015/result.json"
    original_hash = hashlib.sha256(original.read_bytes()).hexdigest()
    rng = np.random.default_rng(seed)
    observations = []
    started = time.monotonic()
    for graph_index in range(graph_count):
        edges = simple_3_regular(n, rng)
        state, cuts = qaoa_state(n, edges, beta, gamma)
        baseline = float(np.dot(np.abs(state) ** 2, cuts))
        pair = greedy_k_independent(n, edges, 3)
        conditioned, probability = conditioned_expectation(state, cuts, pair)
        feasible = pair is not None and conditioned is not None
        observations.append({
            "graph_index": graph_index,
            "edges": edges,
            "a1_pair": pair,
            "baseline_expected_cut": baseline,
            "conditioned_expected_cut": conditioned,
            "conditioning_probability": probability,
            "feasible": feasible,
            "paired_delta": None if not feasible else conditioned - baseline,
            "setup_failure_code": None if feasible else "no_distance_ge_3_pair",
        })
    valid = [row for row in observations if row["feasible"]]
    deltas = [row["paired_delta"] for row in valid]
    mean = lambda values: float(np.mean(values)) if values else None
    sd = float(np.std(deltas, ddof=1)) if len(deltas) > 1 else None
    summary = {
        "graph_count": graph_count,
        "outcomes_retained": len(observations),
        "all_graph_feasibility": len(valid) == graph_count,
        "infeasible_graph_indices": [row["graph_index"] for row in observations if not row["feasible"]],
        "baseline_expected_cut_mean": mean([row["baseline_expected_cut"] for row in observations]),
        "conditioned_expected_cut_mean": mean([row["conditioned_expected_cut"] for row in valid]),
        "paired_delta": {"n": len(deltas), "mean": mean(deltas), "sample_sd": sd,
                         "standard_error": None if not sd else sd / math.sqrt(len(deltas)),
                         "positive_count": sum(x > 0 for x in deltas),
                         "negative_count": sum(x < 0 for x in deltas),
                         "zero_count": sum(x == 0 for x in deltas)},
        "conditioning_probability": {"mean": mean([row["conditioning_probability"] for row in valid]),
                                      "min": min((row["conditioning_probability"] for row in valid), default=None),
                                      "max": max((row["conditioning_probability"] for row in valid), default=None)},
    }
    status = "setup_infeasible" if not summary["all_graph_feasibility"] else ("replication_positive" if summary["paired_delta"]["mean"] > 0 else "replication_nonpositive")
    result = {
        "experiment_id": "EXP-PAPER4-QAOA-A1-INDEPENDENT-REPLICATION-20261015",
        "replication_of": "EXP-PAPER4-QAOA-A1-LARGER-N-ROBUSTNESS-20261015",
        "original_result_sha256": original_hash,
        "evidence_tier": "tier_4_local_exact_state_vector_independent_replication",
        "sources_and_data": ["results/qaoa_source_baseline_larger_n_20261015/result.json", "scripts/run_qaoa_postselection_pilot.py"],
        "hypothesis": "The fixed source-style A1 postselection rule has a positive paired expected-cut delta on a new n=10 graph sample.",
        "competing_explanation": "The earlier positive delta is graph-seed-specific or induced by the fixed graph family, pair rule, or parameter convention.",
        "method": "Exact NumPy state-vector simulation on 20 new simple 3-regular n=10 graphs using the unchanged beta/gamma, distance-ge-3 lexicographic pair rule, alternating assignment, and graph-level paired outcome.",
        "configuration": {"vertices": n, "graphs": graph_count, "seed": seed, "beta": beta, "gamma": gamma,
                           "distance_threshold": 3, "pair_rule": "lexicographically first pair with graph distance >= 3",
                           "state_convention": "exp(-i beta H_B/2) exp(-i gamma H_C/2), H_C=-cut",
                           "assignment": "alternating +1,-1 / bits 0,1", "graph_generator": "rejection-sampled simple 3-regular configuration model"},
        "metrics": {"outcome": "paired conditioned-minus-unconditioned expected cut", "secondary": ["conditioning probability", "positive/negative graph count"], "uncertainty_unit": "independent generated graph"},
        "summary": summary,
        "falsification_gate": {"status": status, "rule": "Falsify this bounded replication if all-graph feasibility fails or the paired mean delta is non-positive; do not reinterpret a negative replication as a failed build."},
        "limitations": ["This is a finite local exact simulation, not hardware or physical-runtime evidence.", "The graph family, parameter choice, pair rule and assignment are inherited unchanged; no post hoc tuning was performed.", "A positive replication does not establish quantum advantage, general QAOA behavior, or Paper 4 planner superiority."],
        "uncertainty": ["Graph-level sample SD/SE are descriptive over these 20 new seeded units only.", "The 0.25 conditioning probability is a state-vector probability, not an end-to-end sampling throughput estimate.", "The result must be paired with the fair shot-budget comparison before any practical efficacy interpretation."],
        "observed_result_or_blocker": "All generated graphs and raw per-graph observations are retained; the independent replication status and paired effect are reported in summary.",
        "next_falsifiable_action": "Compare the complete procedure against unconditioned QAOA under a fixed state-preparation and shot budget; treat conditional state quality and end-to-end best-cut performance separately.",
        "wall_seconds": round(time.monotonic() - started, 4),
        "observations": observations,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"experiment_id": result["experiment_id"], "summary": summary, "falsification_gate": result["falsification_gate"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
