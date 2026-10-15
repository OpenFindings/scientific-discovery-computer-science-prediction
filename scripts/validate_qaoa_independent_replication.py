#!/usr/bin/env python3
"""Independent arithmetic and convention checks for the second QAOA run."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def direct_cut(bitstring: int, edges: list[list[int]]) -> int:
    return sum(((bitstring >> a) & 1) != ((bitstring >> b) & 1) for a, b in edges)


def direct_state(n: int, edges: list[list[int]], beta: float, gamma: float) -> np.ndarray:
    size = 1 << n
    cuts = np.array([direct_cut(x, edges) for x in range(size)], dtype=float)
    state = np.full(size, 1 / math.sqrt(size), dtype=np.complex128) * np.exp(0.5j * gamma * cuts)
    c, s = math.cos(beta / 2), math.sin(beta / 2)
    for q in range(n):
        matrix = np.eye(size, dtype=np.complex128)
        for base in range(size):
            if base & (1 << q):
                continue
            partner = base | (1 << q)
            matrix[base, base] = c
            matrix[base, partner] = -1j * s
            matrix[partner, base] = -1j * s
            matrix[partner, partner] = c
        state = matrix @ state
    return state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("results/qaoa_source_baseline_replication_20261015/result.json"))
    parser.add_argument("--output", type=Path, default=Path("reports/qaoa_independent_replication_validation_20261015.json"))
    args = parser.parse_args()
    result = json.loads(args.input.read_text(encoding="utf-8"))
    observations = result.get("observations", [])
    checks = {
        "experiment_id": result.get("experiment_id") == "EXP-PAPER4-QAOA-A1-INDEPENDENT-REPLICATION-20261015",
        "new_seed": result.get("configuration", {}).get("seed") == 20261016,
        "new_graph_count": len(observations) == 20,
        "all_graph_indices_unique": len({row.get("graph_index") for row in observations}) == 20,
        "all_edges_simple_3_regular": all(len(row.get("edges", [])) == 15 and len({tuple(edge) for edge in row.get("edges", [])}) == 15 and all(a != b for a, b in row.get("edges", [])) for row in observations),
        "all_observations_retained": result.get("summary", {}).get("outcomes_retained") == 20,
        "raw_rows_reconcile": all((row.get("paired_delta") is None or abs(row["paired_delta"] - (row["conditioned_expected_cut"] - row["baseline_expected_cut"])) < 1e-12) for row in observations),
        "no_nan_payload": "NaN" not in json.dumps(result, allow_nan=False),
    }
    row = observations[0] if observations else {}
    try:
        state = direct_state(10, row["edges"], result["configuration"]["beta"], result["configuration"]["gamma"])
        cuts = np.array([direct_cut(x, row["edges"]) for x in range(1 << 10)], dtype=float)
        baseline = float(np.dot(np.abs(state) ** 2, cuts))
        checks["independent_small_row_recomputation"] = abs(baseline - row["baseline_expected_cut"]) < 1e-10
        checks["state_norm"] = abs(float(np.vdot(state, state).real) - 1.0) < 1e-10
    except (KeyError, TypeError, ValueError):
        checks["independent_small_row_recomputation"] = False
        checks["state_norm"] = False
    output = {
        "validation_id": "VALIDATE-EXP-PAPER4-QAOA-A1-INDEPENDENT-REPLICATION-20261015",
        "input": str(args.input),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "scientific_interpretation": "This validates the frozen state-vector convention, graph retention and arithmetic for the independent replication; it does not establish practical advantage or novelty.",
        "unresolved": ["Equal-cost end-to-end best-cut performance is evaluated separately.", "The cited source may already imply the conditional state-quality effect; this run is a replication until a primary-source novelty audit says otherwise."],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if output["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
