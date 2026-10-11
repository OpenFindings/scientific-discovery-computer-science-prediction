from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EvidenceKind(str, Enum):
    FACT = "fact"
    OBSERVATION = "observation"
    INTERPRETATION = "interpretation"
    TEST_RESULT = "test_result"


class NodeKind(str, Enum):
    PAPER = "paper"
    DATASET = "dataset"
    OBSERVATION = "observation"
    CLAIM = "claim"
    HYPOTHESIS = "hypothesis"
    EXPERIMENT = "experiment"
    ARTIFACT = "software_artifact"
    TEST_RESULT = "test_result"


@dataclass(frozen=True)
class Hypothesis:
    id: str
    statement: str
    prior: float


@dataclass(frozen=True)
class Action:
    id: str
    description: str
    tests: tuple[str, ...]
    cost: float
    tractability: float = 1.0
    expected_outcomes: dict[str, dict[str, float]] = field(default_factory=dict)
    provenance_roots: tuple[str, ...] = ()


@dataclass(frozen=True)
class Evidence:
    id: str
    action_id: str
    kind: EvidenceKind
    observation: dict[str, Any]
    source: str
    source_version: str
    timestamp: str
    independent_group: str
    uncertainty: float = 0.0
    interpretation: str | None = None


@dataclass(frozen=True)
class ResearchQuestion:
    id: str
    domain: str
    objective: str
    hypotheses: tuple[Hypothesis, ...]
    actions: tuple[Action, ...]
    constraints: dict[str, Any]
    ground_truth_policy: str
