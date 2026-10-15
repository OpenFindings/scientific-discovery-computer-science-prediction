#!/usr/bin/env python3
"""Run the frozen finite EDCS lazy-repair search.

The runner writes raw JSONL state traces and a compact summary. It does not
touch canonical research state or task queues; reconciliation is supervisor-
owned and happens only after independent validation.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import resource
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/edcs_lazy_repair_counterexample_20261015"
BETA = 4
BETA_MINUS = 3
REPAIR_FLIPS_PER_UPDATE = 1
SEED = 20261015


def edge_key(edge: tuple[int, int]) -> tuple[int, int]:
    return edge


def all_edges(k: int) -> list[tuple[int, int]]:
    return [(u, v) for u in range(k) for v in range(k)]


def max_matching_dp(k: int, edges: set[tuple[int, int]]) -> int:
    """Exact runner oracle: left-subset dynamic program over right masks."""
    adjacency = [[v for v in range(k) if (u, v) in edges] for u in range(k)]
    dp = {0: 0}
    for u in range(k):
        nxt = dict(dp)
        for mask, value in dp.items():
            for v in adjacency[u]:
                bit = 1 << v
                if not mask & bit:
                    nxt[mask | bit] = max(nxt.get(mask | bit, 0), value + 1)
        dp = nxt
    return max(dp.values(), default=0)


@dataclass
class LazyEDCS:
    k: int
    graph: set[tuple[int, int]]
    subgraph: set[tuple[int, int]]
    dirty: deque[tuple[str, int]]

    @classmethod
    def empty(cls, k: int) -> "LazyEDCS":
        return cls(k, set(), set(), deque())

    def clone(self) -> "LazyEDCS":
        return LazyEDCS(self.k, set(self.graph), set(self.subgraph), deque(self.dirty))

    def degree(self, vertex: tuple[str, int]) -> int:
        side, index = vertex
        if side == "L":
            return sum(u == index for u, _ in self.subgraph)
        return sum(v == index for _, v in self.subgraph)

    def delta(self, edge: tuple[int, int]) -> int:
        return self.degree(("L", edge[0])) + self.degree(("R", edge[1]))

    def enqueue(self, vertices: Iterable[tuple[str, int]]) -> None:
        existing = set(self.dirty)
        for vertex in vertices:
            if vertex not in existing:
                self.dirty.append(vertex)
                existing.add(vertex)

    def incident_violation(self, vertex: tuple[str, int]) -> tuple[str, tuple[int, int], int] | None:
        edges = sorted([edge for edge in self.graph if (vertex[0] == "L" and edge[0] == vertex[1])
                        or (vertex[0] == "R" and edge[1] == vertex[1])], key=edge_key)
        p1 = [("P1", edge, self.delta(edge)) for edge in edges
              if edge in self.subgraph and self.delta(edge) > BETA]
        if p1:
            return min(p1, key=lambda row: row[1])
        p2 = [("P2", edge, self.delta(edge)) for edge in edges
              if edge not in self.subgraph and self.delta(edge) < BETA_MINUS]
        if p2:
            return min(p2, key=lambda row: row[1])
        return None

    def repair_once(self) -> dict:
        flips = []
        while self.dirty and len(flips) < REPAIR_FLIPS_PER_UPDATE:
            vertex = self.dirty[0]
            violation = self.incident_violation(vertex)
            if violation is None:
                self.dirty.popleft()
                continue
            kind, edge, before_delta = violation
            if kind == "P1":
                self.subgraph.remove(edge)
            else:
                self.subgraph.add(edge)
            self.enqueue((("L", edge[0]), ("R", edge[1])))
            flips.append({"kind": kind, "edge": list(edge), "before_delta": before_delta})
        return {"flips": flips, "dirty_after_repair": [[s, i] for s, i in self.dirty]}

    def update(self, operation: str, edge: tuple[int, int]) -> dict:
        before_h = sorted(self.subgraph)
        if operation == "insert":
            if edge in self.graph:
                raise ValueError("duplicate insertion")
            self.graph.add(edge)
            self.enqueue((("L", edge[0]), ("R", edge[1])))
        elif operation == "delete":
            if edge not in self.graph:
                raise ValueError("delete of absent edge")
            self.graph.remove(edge)
            if edge in self.subgraph:
                self.subgraph.remove(edge)
                self.enqueue((("L", edge[0]), ("R", edge[1])))
        else:
            raise ValueError(operation)
        repair = self.repair_once()
        return {"operation": operation, "edge": list(edge), "H_before": [list(e) for e in before_h], **repair}

    def violations(self) -> list[dict]:
        rows = []
        for edge in sorted(self.graph):
            delta = self.delta(edge)
            if edge in self.subgraph and delta > BETA:
                rows.append({"kind": "P1", "edge": list(edge), "degree_sum": delta,
                             "threshold": BETA, "used": True})
            if edge not in self.subgraph and delta < BETA_MINUS:
                rows.append({"kind": "P2", "edge": list(edge), "degree_sum": delta,
                             "threshold": BETA_MINUS, "used": False})
        return rows


def state_record(engine: LazyEDCS, update_index: int, context: str, update: dict, sequence: list[dict]) -> dict:
    mu_g = max_matching_dp(engine.k, engine.graph)
    mu_h = max_matching_dp(engine.k, engine.subgraph)
    violations = engine.violations()
    ratio = None if mu_g == 0 else mu_h / mu_g
    failure = bool(violations) or (ratio is not None and ratio < 2 / 3)
    relevant = []
    for row in violations:
        edge = tuple(row["edge"])
        relevant.append({"kind": row["kind"], "edge": row["edge"], "degree_left": engine.degree(("L", edge[0])),
                         "degree_right": engine.degree(("R", edge[1])), "degree_sum": row["degree_sum"],
                         "threshold": row["threshold"]})
    return {
        "k": engine.k,
        "context": context,
        "update_index": update_index,
        "update": update,
        "sequence": sequence,
        "G": [list(e) for e in sorted(engine.graph)],
        "H": [list(e) for e in sorted(engine.subgraph)],
        "mu_G": mu_g,
        "mu_H": mu_h,
        "matching_ratio": ratio,
        "violations": violations,
        "relevant_degree_sums": relevant,
        "failed": failure,
        "dirty_after_state": [[s, i] for s, i in engine.dirty],
    }


def run_sequence(k: int, updates: list[tuple[str, tuple[int, int]]], context: str, trace_file) -> tuple[int, dict | None, int]:
    engine = LazyEDCS.empty(k)
    sequence = []
    records = 0
    first_failure = None
    for index, (operation, edge) in enumerate(updates):
        update = engine.update(operation, edge)
        sequence.append({"operation": operation, "edge": list(edge)})
        record = state_record(engine, index, context, update, sequence)
        trace_file.write(json.dumps(record, sort_keys=True) + "\n")
        records += 1
        if record["failed"] and first_failure is None:
            first_failure = record
    return records, first_failure, len(updates)


def complete_setup_then_deletions(k: int, deletion_order: tuple[tuple[int, int], ...]) -> list[tuple[str, tuple[int, int]]]:
    return [("insert", edge) for edge in all_edges(k)] + [("delete", edge) for edge in deletion_order]


def greedy_mixed_sequence(k: int, depth: int) -> list[tuple[str, tuple[int, int]]]:
    engine = LazyEDCS.empty(k)
    chosen = []
    for _ in range(depth):
        candidates = []
        edges = all_edges(k)
        for edge in edges:
            if edge in engine.graph:
                candidates.append(("delete", edge))
            else:
                candidates.append(("insert", edge))
        scored = []
        for operation, edge in candidates:
            trial = engine.clone()
            trial.update(operation, edge)
            violations = len(trial.violations())
            trial_mu_g = max_matching_dp(k, trial.graph)
            trial_ratio = 1.0 if trial_mu_g == 0 else max_matching_dp(k, trial.subgraph) / trial_mu_g
            ratio_gap = 0 if trial.violations() else max(0, 2 / 3 - trial_ratio)
            scored.append((violations, ratio_gap, operation, edge))
        _, _, operation, edge = max(scored, key=lambda row: (row[0], row[1], row[2] == "delete", row[3]))
        engine.update(operation, edge)
        chosen.append((operation, edge))
    return chosen


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (120, 120))
        resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024 * 1024, 1024 * 1024 * 1024))
    except (OSError, ValueError):
        pass
    script_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    started = time.monotonic()
    trace_path = OUT / "raw_trace.jsonl"
    summary = {
        "experiment_id": "EXP-EDCS-LAZY-REPAIR-INVARIANT-20261015",
        "protocol_id": "EDCS-LAZY-REPAIR-PROTOCOL-V1",
        "implementation_sha256": script_hash,
        "seed": SEED,
        "parameters": {"beta": BETA, "beta_minus": BETA_MINUS, "repair_flips_per_update": REPAIR_FLIPS_PER_UPDATE},
        "domains": {"static_k": [1, 2, 3], "deletion_k": 3, "deletion_prefix_max": 6, "greedy_mixed_depth": 6},
        "started_at_monotonic": started,
        "static_graphs": 0,
        "static_updates": 0,
        "deletion_sequences": 0,
        "deletion_updates": 0,
        "greedy_updates": 0,
        "first_failure": None,
        "outcome": "running",
    }
    with trace_path.open("w", encoding="utf-8") as trace_file:
        for k in (1, 2, 3):
            for mask in range(1 << (k * k)):
                edges = all_edges(k)
                updates = [("insert", edge) for i, edge in enumerate(edges) if mask & (1 << i)]
                records, failure, _ = run_sequence(k, updates, f"static_all_masks_k{k}_mask{mask}", trace_file)
                summary["static_graphs"] += 1
                summary["static_updates"] += records
                if failure is not None and summary["first_failure"] is None:
                    summary["first_failure"] = failure
        deletion_edges = all_edges(3)
        for length in range(1, 7):
            for order in itertools.permutations(deletion_edges, length):
                records, failure, _ = run_sequence(3, complete_setup_then_deletions(3, order),
                                                    f"K3_3_deletion_prefix_len{length}", trace_file)
                summary["deletion_sequences"] += 1
                summary["deletion_updates"] += records
                if failure is not None and summary["first_failure"] is None:
                    summary["first_failure"] = failure
        mixed = greedy_mixed_sequence(3, 6)
        records, failure, _ = run_sequence(3, mixed, "greedy_mixed_adversary_seed20261015", trace_file)
        summary["greedy_updates"] = records
        summary["greedy_sequence"] = [{"operation": op, "edge": list(edge)} for op, edge in mixed]
        if failure is not None and summary["first_failure"] is None:
            summary["first_failure"] = failure
    summary["elapsed_seconds"] = time.monotonic() - started
    summary["outcome"] = "counterexample_found" if summary["first_failure"] else "no_failure_in_declared_finite_domain"
    summary["raw_trace_sha256"] = hashlib.sha256(trace_path.read_bytes()).hexdigest()
    summary["resource_limits"] = {"cpu_seconds_max": 120, "memory_mib_max": 1024, "processes": 1, "network": False}
    (OUT / "result.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
