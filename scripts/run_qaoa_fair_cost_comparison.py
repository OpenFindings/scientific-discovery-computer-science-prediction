#!/usr/bin/env python3
"""Compare complete QAOA procedures under a fixed shot/state-preparation budget."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.run_qaoa_postselection_pilot import conditioned_expectation, greedy_k_independent, qaoa_state  # noqa: E402


def cut_values(n: int, edges: list[list[int]]) -> np.ndarray:
    return np.array([sum(((x >> a) & 1) != ((x >> b) & 1) for a, b in edges) for x in range(1 << n)], dtype=int)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replication", type=Path, default=Path("results/qaoa_source_baseline_replication_20261015/result.json"))
    parser.add_argument("--output", type=Path, default=Path("results/qaoa_fair_cost_comparison_20261015/result.json"))
    args = parser.parse_args()
    replication = json.loads(args.replication.read_text(encoding="utf-8"))
    n, shots, repeats, seed = 10, 400, 64, 20261017
    beta, gamma = replication["configuration"]["beta"], replication["configuration"]["gamma"]
    rng = np.random.default_rng(seed)
    rows = []
    for source_row in replication["observations"]:
        edges = source_row["edges"]
        cuts = cut_values(n, edges)
        state, _ = qaoa_state(n, [tuple(edge) for edge in edges], beta, gamma)
        probs = np.abs(state) ** 2
        pair = tuple(source_row["a1_pair"])
        accepted = np.array([((x >> pair[0]) & 1) == 0 and ((x >> pair[1]) & 1) == 1 for x in range(1 << n)])
        standard_best, post_best, accepted_counts, discarded_counts, matched_budget_best = [], [], [], [], []
        # A/B use the same 400 state preparations; C gives standard QAOA the
        # 1/p preparation budget needed to obtain about 400 accepted shots.
        matched_shots = int(round(shots / source_row["conditioning_probability"]))
        for _ in range(repeats):
            standard_samples = rng.choice(len(probs), size=shots, p=probs)
            post_samples = rng.choice(len(probs), size=shots, p=probs)
            matched_samples = rng.choice(len(probs), size=matched_shots, p=probs)
            standard_best.append(int(np.max(cuts[standard_samples])))
            keep = post_samples[accepted[post_samples]]
            post_best.append(None if len(keep) == 0 else int(np.max(cuts[keep])))
            accepted_counts.append(int(len(keep)))
            discarded_counts.append(int(shots - len(keep)))
            matched_budget_best.append(int(np.max(cuts[matched_samples])))
        rows.append({
            "graph_index": source_row["graph_index"],
            "shots_standard_and_postselected": shots,
            "matched_standard_shots_for_approximately_equal_accepted_budget": matched_shots,
            "standard_best_cut_mean": float(np.mean(standard_best)),
            "postselected_best_cut_mean": float(np.mean([x for x in post_best if x is not None])),
            "matched_budget_standard_best_cut_mean": float(np.mean(matched_budget_best)),
            "postselected_no_acceptance_count": int(sum(x is None for x in post_best)),
            "accepted_count_mean": float(np.mean(accepted_counts)),
            "discarded_count_mean": float(np.mean(discarded_counts)),
            "postselected_minus_standard": float(np.mean([x for x in post_best if x is not None]) - np.mean(standard_best)),
            "postselected_minus_matched_budget_standard": float(np.mean([x for x in post_best if x is not None]) - np.mean(matched_budget_best)),
        })
    post = np.array([row["postselected_best_cut_mean"] for row in rows])
    standard = np.array([row["standard_best_cut_mean"] for row in rows])
    matched = np.array([row["matched_budget_standard_best_cut_mean"] for row in rows])
    result = {
        "experiment_id": "EXP-PAPER4-QAOA-FAIR-SHOT-COST-20261015",
        "replication_input_sha256": hashlib.sha256(args.replication.read_bytes()).hexdigest(),
        "evidence_tier": "tier_4_local_shot_budget_end_to_end_comparison",
        "hypothesis": "The conditional A1 state-quality effect yields a higher complete-procedure best-cut outcome under equal state-preparation budget.",
        "competing_explanation": "Postselection raises conditional state quality but loses too many samples, so standard sampling matches or exceeds end-to-end best cut under equal preparation cost.",
        "method": "Monte Carlo measurement of the exact replicated state distributions on the same 20 new graph units; A standard and B postselected procedures each receive 400 preparations, while C receives 400/p preparations as a matched accepted-shot-cost reference.",
        "configuration": {"graphs": 20, "n": n, "shots_per_procedure": shots, "repeats_per_graph": repeats, "measurement_seed": seed, "beta": beta, "gamma": gamma, "physical_runtime_identifiable": False, "cost_proxy": "state preparations / measurements / retained samples"},
        "metrics": {"primary": "graph-level mean best cut after fixed preparation budget", "secondary": ["accepted samples", "discarded samples", "no-acceptance failures", "matched-budget standard reference"], "uncertainty_unit": "independent graph"},
        "summary": {"graphs": len(rows), "postselected_minus_standard_mean": float(np.mean(post - standard)), "postselected_minus_matched_budget_standard_mean": float(np.mean(post - matched)), "positive_vs_standard": int(np.sum(post > standard)), "positive_vs_matched_budget_standard": int(np.sum(post > matched)), "postselected_no_acceptance_total": int(sum(row["postselected_no_acceptance_count"] for row in rows)), "mean_accepted_count": float(np.mean([row["accepted_count_mean"] for row in rows])), "mean_discarded_count": float(np.mean([row["discarded_count_mean"] for row in rows]))},
        "falsification_gate": {"status": "end_to_end_advantage_not_supported" if float(np.mean(post - standard)) <= 0 else "conditional_end_to_end_advantage_in_this_budget", "rule": "Do not call conditional state quality a practical advantage unless the complete postselected procedure exceeds equal-preparation standard QAOA; never call this quantum speedup."},
        "limitations": ["Exact simulation cannot identify physical runtime, hardware noise, queueing or measurement cost.", "The shot-count result is a bounded graph-family and fixed-parameter comparison, not a general optimizer or quantum-advantage claim.", "Monte Carlo repeats are nested within fixed graph units; graph-level variation remains the conservative uncertainty unit."],
        "uncertainty": ["All procedures use the same exact state convention and graph sample, but postselection uses fewer retained samples by design.", "C is a declared matched-preparation reference with approximately 400 accepted-shot-equivalent preparations, not a separate quantum algorithm.", "A positive conditional result can coexist with a non-positive end-to-end result."],
        "observed_result_or_blocker": "The complete procedure comparison is reported with all 20 graph rows, raw count summaries and the predeclared shot-cost accounting.",
        "next_falsifiable_action": "If the end-to-end gate is non-positive, retain the conditional state-quality observation as a reproduction only; if positive, rerun one fresh shot seed before any stronger claim.",
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"experiment_id": result["experiment_id"], "summary": result["summary"], "falsification_gate": result["falsification_gate"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
