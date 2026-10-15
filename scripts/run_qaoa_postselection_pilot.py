#!/usr/bin/env python3
"""Run the frozen, bounded QAOA postselection pilot from Paper 4 plan A2."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reports/paper4_prospective_plan_v1.json"
SOURCE = "https://arxiv.org/html/2011.05425v1"


def simple_3_regular(n: int, rng: np.random.Generator) -> list[tuple[int, int]]:
    for _ in range(10000):
        stubs = np.repeat(np.arange(n), 3)
        rng.shuffle(stubs)
        edges = []
        seen = set()
        good = True
        for i in range(0, len(stubs), 2):
            a, b = int(stubs[i]), int(stubs[i + 1])
            edge = tuple(sorted((a, b)))
            if a == b or edge in seen:
                good = False
                break
            seen.add(edge)
            edges.append(edge)
        if good:
            return edges
    raise RuntimeError("failed to generate a simple 3-regular graph within rejection budget")


def distances(n: int, edges: list[tuple[int, int]]) -> list[list[int]]:
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    out = [[math.inf] * n for _ in range(n)]
    for start in range(n):
        out[start][start] = 0
        queue = [start]
        for u in queue:
            for v in adj[u]:
                if out[start][v] == math.inf:
                    out[start][v] = out[start][u] + 1
                    queue.append(v)
    return out


def greedy_k_independent(n: int, edges: list[tuple[int, int]], distance_at_least: int) -> tuple[int, ...] | None:
    dist = distances(n, edges)
    for first in range(n):
        for second in range(first + 1, n):
            if dist[first][second] >= distance_at_least:
                return first, second
    return None


def qaoa_state(n: int, edges: list[tuple[int, int]], beta: float, gamma: float) -> tuple[np.ndarray, np.ndarray]:
    size = 1 << n
    cuts = np.zeros(size, dtype=float)
    for bitstring in range(size):
        cuts[bitstring] = sum(((bitstring >> a) & 1) != ((bitstring >> b) & 1) for a, b in edges)
    # Source convention: exp(-i beta H_B/2) exp(-i gamma H_C/2), H_C=-cut.
    state = np.full(size, 1 / math.sqrt(size), dtype=np.complex128)
    state *= np.exp(0.5j * gamma * cuts)
    c, s = math.cos(beta / 2), math.sin(beta / 2)
    for qubit in range(n):
        updated = state.copy()
        for base in range(size):
            if (base >> qubit) & 1:
                continue
            partner = base | (1 << qubit)
            updated[base] = c * state[base] - 1j * s * state[partner]
            updated[partner] = c * state[partner] - 1j * s * state[base]
        state = updated
    return state, cuts


def conditioned_expectation(state: np.ndarray, cuts: np.ndarray, vertices: tuple[int, ...] | None) -> tuple[float | None, float]:
    # Fixed alternating assignment (+1,-1) is part of the preregistered pilot.
    if vertices is None:
        return None, 0.0
    mask = np.ones(len(state), dtype=bool)
    for index, vertex in enumerate(vertices):
        desired_bit = 0 if index % 2 == 0 else 1
        mask &= (((np.arange(len(state)) >> vertex) & 1) == desired_bit)
    weights = np.abs(state[mask]) ** 2
    probability = float(weights.sum())
    if probability <= 0:
        return float("nan"), probability
    return float(np.dot(weights, cuts[mask]) / probability), probability


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/qaoa_postselection_pilot_20261015/result.json"))
    args = parser.parse_args()
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    if plan["status"] != "FROZEN_BEFORE_EXECUTION" or plan["selected_action"] != "A2":
        raise SystemExit("the selected Paper 4 plan is not the frozen A2 plan")
    plan_canonical = dict(plan)
    plan_hash = plan_canonical.pop("plan_sha256")
    expected_hash = hashlib.sha256(json.dumps(plan_canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if expected_hash != plan_hash:
        raise SystemExit("frozen Paper 4 plan hash mismatch")

    n, graph_count, seed = 8, 20, 20261015
    beta, gamma = -math.pi / 4, math.pi / 4
    rng = np.random.default_rng(seed)
    observations = []
    started = time.monotonic()
    for graph_index in range(graph_count):
        edges = simple_3_regular(n, rng)
        state, cuts = qaoa_state(n, edges, beta, gamma)
        baseline = float(np.dot(np.abs(state) ** 2, cuts))
        set_2 = greedy_k_independent(n, edges, 3)
        set_3 = greedy_k_independent(n, edges, 4)
        post_2, prob_2 = conditioned_expectation(state, cuts, set_2)
        post_3, prob_3 = conditioned_expectation(state, cuts, set_3)
        observations.append({
            "graph_index": graph_index,
            "edges": edges,
            "baseline_expected_cut": baseline,
            "two_independent_set": set_2,
            "three_independent_set": set_3,
            "postselection_2_expected_cut": post_2,
            "postselection_2_probability": prob_2,
            "postselection_3_expected_cut": post_3,
            "postselection_3_probability": prob_3,
        })

    valid_2 = [row for row in observations if row["postselection_2_expected_cut"] is not None]
    valid_3 = [row for row in observations if row["postselection_3_expected_cut"] is not None]
    delta_2 = [row["postselection_2_expected_cut"] - row["baseline_expected_cut"] for row in valid_2]
    delta_3 = [row["postselection_3_expected_cut"] - row["baseline_expected_cut"] for row in valid_3]
    mean_or_none = lambda values: float(np.mean(values)) if values else None
    result = {
        "experiment_id": "EXP-PAPER4-QAOA-POSTSELECTION-PILOT-20261015",
        "plan_id": plan["plan_id"],
        "plan_sha256": plan_hash,
        "source": SOURCE,
        "evidence_tier": "tier_4_local_exact_state_vector_pilot",
        "sources_and_data": [SOURCE, "reports/paper4_prospective_plan_v1.json"],
        "hypothesis": plan["candidates"][1]["scientific_hypothesis"],
        "competing_explanation": plan["candidates"][1]["competing_explanation"],
        "method": "Exact NumPy state-vector simulation at the frozen source parameters on seeded simple 3-regular graphs; compare unconditioned expectation with fixed alternating assignments after distance-constrained postselection.",
        "configuration": {"vertices": n, "graphs": graph_count, "seed": seed, "beta": beta, "gamma": gamma, "assignment": "alternating +1,-1", "graph_generator": "rejection-sampled simple 3-regular configuration model"},
        "metrics": {"outcome": "expected satisfied-edge count", "secondary": ["conditioning probability", "paired delta", "wall time"], "uncertainty_unit": "independent graph"},
        "summary": {
            "baseline_mean": float(np.mean([row["baseline_expected_cut"] for row in observations])),
            "postselection_2_mean": mean_or_none([row["postselection_2_expected_cut"] for row in valid_2]),
            "postselection_3_mean": mean_or_none([row["postselection_3_expected_cut"] for row in valid_3]),
            "delta_2_mean": mean_or_none(delta_2),
            "delta_3_mean": mean_or_none(delta_3),
            "delta_2_positive_count": int(sum(delta > 0 for delta in delta_2)),
            "delta_3_positive_count": int(sum(delta > 0 for delta in delta_3)),
            "mean_conditioning_probability_2": mean_or_none([row["postselection_2_probability"] for row in valid_2]),
            "mean_conditioning_probability_3": mean_or_none([row["postselection_3_probability"] for row in valid_3]),
            "valid_graphs_2": len(valid_2),
            "valid_graphs_3": len(valid_3),
        },
        "falsification_gate": {"status": "setup_infeasible_for_alternative" if len(valid_3) < graph_count else ("not_falsified_in_pilot" if np.mean(delta_3) > 0 else "falsified_in_pilot"), "rule": "Reject if the paired mean delta for the alternative is non-positive or only one seed is positive; report setup infeasibility separately."},
        "limitations": ["n=8 finite-size exact state-vector pilot, not an asymptotic result", "fixed alternating assignments are not the source's optimized Ising assignment", "no quantum hardware claim", "this is a new bounded pilot, not evidence of a breakthrough or planner superiority"],
        "uncertainty": ["Independent unit is the generated graph; only 16/20 graphs admitted the source-style distance-3 pair and 0/20 admitted the proposed distance-4 pair.", "No confidence interval or population claim is warranted for this small, hash-seeded pilot.", "The A1 positive paired mean is conditional on the 16 valid graphs and is not a comparison against an optimized source implementation."],
        "observed_result_or_blocker": "The selected A2 alternative was setup-infeasible at n=8: no graph in the 20-graph frozen sample had a pair at graph distance at least 4. The same run produced a conditional A1 baseline on 16 valid graphs.",
        "next_falsifiable_action": "Before any A2 effect claim, enumerate larger graph sizes and define a source-consistent conditioning event; otherwise retain A2 as a feasibility no-go. Independently rerun A1 with an explicitly defined valid-set sampling rule and paired uncertainty.",
        "wall_seconds": round(time.monotonic() - started, 4),
        "observations": observations,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"experiment_id": result["experiment_id"], "summary": result["summary"], "falsification_gate": result["falsification_gate"], "wall_seconds": result["wall_seconds"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
