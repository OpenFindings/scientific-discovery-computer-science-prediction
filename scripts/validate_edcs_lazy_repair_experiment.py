#!/usr/bin/env python3
"""Independently validate the EDCS lazy-repair experiment trace."""
from __future__ import annotations

import hashlib
import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/edcs_lazy_repair_counterexample_20261015"
BETA = 4
BETA_MINUS = 3


def degrees(k: int, h: set[tuple[int, int]]) -> tuple[list[int], list[int]]:
    left = [0] * k
    right = [0] * k
    for u, v in h:
        left[u] += 1
        right[v] += 1
    return left, right


def independent_matching(k: int, edges: set[tuple[int, int]]) -> int:
    """Independent exact oracle: recursive augmenting search, not runner DP."""
    adjacency = [[v for v in range(k) if (u, v) in edges] for u in range(k)]

    def search(u: int, used: int) -> int:
        if u == k:
            return 0
        best = search(u + 1, used)
        for v in adjacency[u]:
            if not (used >> v) & 1:
                best = max(best, 1 + search(u + 1, used | (1 << v)))
        return best

    return search(0, 0)


def independent_violations(k: int, g: set[tuple[int, int]], h: set[tuple[int, int]]) -> list[dict]:
    left, right = degrees(k, h)
    rows = []
    for edge in sorted(g):
        delta = left[edge[0]] + right[edge[1]]
        if edge in h and delta > BETA:
            rows.append({"kind": "P1", "edge": list(edge), "degree_sum": delta, "threshold": BETA,
                         "degree_left": left[edge[0]], "degree_right": right[edge[1]]})
        if edge not in h and delta < BETA_MINUS:
            rows.append({"kind": "P2", "edge": list(edge), "degree_sum": delta, "threshold": BETA_MINUS,
                         "degree_left": left[edge[0]], "degree_right": right[edge[1]]})
    return rows


def first_independent_failure(record: dict) -> dict | None:
    violations = independent_violations(
        record["k"],
        {tuple(edge) for edge in record["G"]},
        {tuple(edge) for edge in record["H"]},
    )
    k = record["k"]
    mu_g = independent_matching(k, {tuple(edge) for edge in record["G"]})
    mu_h = independent_matching(k, {tuple(edge) for edge in record["H"]})
    ratio_failure = mu_g > 0 and mu_h / mu_g < 2 / 3
    if violations or ratio_failure:
        return {"violations": violations, "mu_G": mu_g, "mu_H": mu_h,
                "matching_ratio": None if mu_g == 0 else mu_h / mu_g,
                "ratio_failure": ratio_failure}
    return None


def replay_variant(k: int, sequence: list[dict]) -> dict | None:
    """Independent replay of the frozen one-flip rule for minimization."""
    graph: set[tuple[int, int]] = set()
    subgraph: set[tuple[int, int]] = set()
    dirty: deque[tuple[str, int]] = deque()

    def enqueue(vertices: list[tuple[str, int]]) -> None:
        for vertex in vertices:
            if vertex not in dirty:
                dirty.append(vertex)

    def degree(vertex: tuple[str, int]) -> int:
        if vertex[0] == "L":
            return sum(u == vertex[1] for u, _ in subgraph)
        return sum(v == vertex[1] for _, v in subgraph)

    def delta(edge: tuple[int, int]) -> int:
        return degree(("L", edge[0])) + degree(("R", edge[1]))

    for index, row in enumerate(sequence):
        operation = row["operation"]
        edge = tuple(row["edge"])
        if operation == "insert":
            if edge in graph:
                return None
            graph.add(edge)
            enqueue([("L", edge[0]), ("R", edge[1])])
        elif operation == "delete":
            if edge not in graph:
                return None
            graph.remove(edge)
            if edge in subgraph:
                subgraph.remove(edge)
                enqueue([("L", edge[0]), ("R", edge[1])])
        else:
            return None

        while dirty:
            vertex = dirty[0]
            incident = sorted(edge for edge in graph if (vertex[0] == "L" and edge[0] == vertex[1])
                              or (vertex[0] == "R" and edge[1] == vertex[1]))
            p1 = [edge for edge in incident if edge in subgraph and delta(edge) > BETA]
            p2 = [edge for edge in incident if edge not in subgraph and delta(edge) < BETA_MINUS]
            if p1:
                chosen = min(p1)
                subgraph.remove(chosen)
                enqueue([("L", chosen[0]), ("R", chosen[1])])
                break
            if p2:
                chosen = min(p2)
                subgraph.add(chosen)
                enqueue([("L", chosen[0]), ("R", chosen[1])])
                break
            dirty.popleft()

        violations = independent_violations(k, graph, subgraph)
        mu_g = independent_matching(k, graph)
        mu_h = independent_matching(k, subgraph)
        if violations or (mu_g > 0 and mu_h / mu_g < 2 / 3):
            return {"update_index": index, "sequence": sequence[:index + 1],
                    "G": [list(edge) for edge in sorted(graph)],
                    "H": [list(edge) for edge in sorted(subgraph)], "violations": violations,
                    "mu_G": mu_g, "mu_H": mu_h,
                    "matching_ratio": None if mu_g == 0 else mu_h / mu_g}
    return None


def minimize_failure(record: dict) -> dict | None:
    sequence = list(record["sequence"])
    if replay_variant(record["k"], sequence) is None:
        return None
    changed = True
    while changed:
        changed = False
        for index in range(len(sequence)):
            candidate = sequence[:index] + sequence[index + 1:]
            if replay_variant(record["k"], candidate) is not None:
                sequence = candidate
                changed = True
                break
    return replay_variant(record["k"], sequence)


def main() -> int:
    result_path = OUT / "result.json"
    trace_path = OUT / "raw_trace.jsonl"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    records = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    checks = {
        "trace_nonempty": bool(records),
        "trace_hash_matches": hashlib.sha256(trace_path.read_bytes()).hexdigest() == result.get("raw_trace_sha256"),
        "runner_script_hash_present": bool(result.get("implementation_sha256")),
        "independent_rows_checked": 0,
        "runner_independent_agreement": True,
        "first_failure_reproduced": True,
    }
    independent_failure = None
    for record in records:
        checks["independent_rows_checked"] += 1
        failure = first_independent_failure(record)
        expected = bool(record.get("failed"))
        if bool(failure) != expected:
            checks["runner_independent_agreement"] = False
        if failure is not None and independent_failure is None:
            independent_failure = {"record": record, "independent": failure}
    expected_failure = result.get("first_failure")
    if bool(expected_failure) != bool(independent_failure):
        checks["first_failure_reproduced"] = False
    elif expected_failure and independent_failure:
        checks["first_failure_reproduced"] = (
            expected_failure["context"] == independent_failure["record"]["context"]
            and expected_failure["update_index"] == independent_failure["record"]["update_index"]
            and expected_failure["violations"] == independent_failure["record"]["violations"]
        )

    minimized = minimize_failure(independent_failure["record"]) if independent_failure else None

    validation = {
        "validation_id": "EDCS-LAZY-REPAIR-VALIDATION-20261015",
        "experiment_id": result.get("experiment_id"),
        "checks": checks,
        "independent_first_failure": independent_failure,
        "minimized_failure": minimized,
        "scientific_success": all(value is True for key, value in checks.items() if key not in {"independent_rows_checked"}),
        "interpretation": (
            "The independent oracle reproduces the finite failure and records the exact violating degree sums."
            if independent_failure else
            "The independent oracle found no failure in the fully enumerated finite trace domain; this is not a proof."
        ),
    }
    (OUT / "independent_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0 if validation["scientific_success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
