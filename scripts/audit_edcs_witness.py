#!/usr/bin/env python3
"""Independently replay the four-edge EDCS witness.

This is a fixed witness checker, not a search and not an experiment.  It uses
its own queue and degree logic so the mathematical note does not depend on the
runner's assertions.
"""
from __future__ import annotations

import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BETA = 4
BETA_MINUS = 3
SEQUENCE = [(0, 0), (0, 1), (0, 2), (1, 0)]


class Witness:
    def __init__(self) -> None:
        self.graph: set[tuple[int, int]] = set()
        self.h: set[tuple[int, int]] = set()
        self.dirty: deque[tuple[str, int]] = deque()

    def enqueue(self, vertices: tuple[tuple[str, int], ...]) -> None:
        known = set(self.dirty)
        for vertex in vertices:
            if vertex not in known:
                self.dirty.append(vertex)
                known.add(vertex)

    def degree(self, vertex: tuple[str, int]) -> int:
        side, index = vertex
        return sum((u == index if side == "L" else v == index) for u, v in self.h)

    def delta(self, edge: tuple[int, int]) -> int:
        return self.degree(("L", edge[0])) + self.degree(("R", edge[1]))

    def repair_once(self) -> dict:
        flips = []
        while self.dirty and not flips:
            vertex = self.dirty[0]
            incident = sorted(
                (edge for edge in self.graph
                 if (vertex[0] == "L" and edge[0] == vertex[1])
                 or (vertex[0] == "R" and edge[1] == vertex[1]))
            )
            p1 = [edge for edge in incident if edge in self.h and self.delta(edge) > BETA]
            p2 = [edge for edge in incident if edge not in self.h and self.delta(edge) < BETA_MINUS]
            if p1:
                edge, kind = p1[0], "P1"
                before_delta = self.delta(edge)
                self.h.remove(edge)
            elif p2:
                edge, kind = p2[0], "P2"
                before_delta = self.delta(edge)
                self.h.add(edge)
            else:
                self.dirty.popleft()
                continue
            self.enqueue((("L", edge[0]), ("R", edge[1])))
            flips.append({"kind": kind, "edge": list(edge), "before_delta": before_delta})
        return {"flips": flips, "dirty_after_repair": [[s, i] for s, i in self.dirty]}

    def update(self, edge: tuple[int, int]) -> dict:
        self.graph.add(edge)
        self.enqueue((("L", edge[0]), ("R", edge[1])))
        return self.repair_once()

    def p1_violations(self) -> list[dict]:
        return [{"edge": list(edge), "degree_sum": self.delta(edge)}
                for edge in sorted(self.graph)
                if edge in self.h and self.delta(edge) > BETA]


def main() -> int:
    witness = Witness()
    rows = []
    for index, edge in enumerate(SEQUENCE):
        repair = witness.update(edge)
        rows.append({
            "update_index": index,
            "inserted": list(edge),
            "H": [list(e) for e in sorted(witness.h)],
            "dirty_after_repair": repair["dirty_after_repair"],
            "flips": repair["flips"],
            "degrees": {
                "L0": witness.degree(("L", 0)),
                "L1": witness.degree(("L", 1)),
                "R0": witness.degree(("R", 0)),
                "R1": witness.degree(("R", 1)),
                "R2": witness.degree(("R", 2)),
            },
            "p1_violations": witness.p1_violations(),
        })
    result = {
        "checker": "independent_fixed_witness_replay",
        "sequence": [list(edge) for edge in SEQUENCE],
        "beta": BETA,
        "beta_minus": BETA_MINUS,
        "rows": rows,
        "first_violation_update_index": next(i for i, row in enumerate(rows) if row["p1_violations"]),
        "first_violation": rows[-1]["p1_violations"][0],
        "conclusion": "The fourth insertion is P2-repaired by adding (1,0), after which (0,0) has degree sum 5 > 4.",
    }
    output = ROOT / "results/edcs_lazy_repair_counterexample_20261015/mathematical_witness_check.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output.relative_to(ROOT)), "first_violation": result["first_violation"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
