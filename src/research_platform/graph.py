from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict
from .models import NodeKind


@dataclass(frozen=True)
class GraphNode:
    id: str
    kind: NodeKind
    data: dict


@dataclass(frozen=True)
class GraphEdge:
    source: str
    relation: str
    target: str
    provenance: str


class EvidenceGraph:
    """Typed evidence graph with explicit provenance and source independence."""

    def __init__(self) -> None:
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []

    def add_node(self, node: GraphNode) -> None:
        if node.id in self.nodes and self.nodes[node.id].kind != node.kind:
            raise ValueError(f"node id reused with a different kind: {node.id}")
        self.nodes[node.id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise KeyError("edges must reference existing nodes")
        self.edges.append(edge)

    def independent_sources(self, node_id: str) -> set[str]:
        groups = set()
        for edge in self.edges:
            if edge.target == node_id:
                groups.add(edge.provenance)
        return groups

    def incoming(self, node_id: str) -> list[GraphEdge]:
        return [edge for edge in self.edges if edge.target == node_id]

