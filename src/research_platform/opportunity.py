"""Versioned question records and evaluation metrics for a future CS transfer.

No CS outcome model or action-utility model has been validated.  Forecast and
ranking entry points fail closed rather than returning hand-weighted scores.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
from typing import Iterable


OUTCOMES = ("attention", "resolution", "premise_revision")
FEATURES = (
    "question_specificity", "evidence_breadth", "explicit_competing_hypotheses",
    "direct_prior_evidence", "explicit_contradiction", "tractability", "novelty",
    "publication_count", "citation_count",
)


@dataclass(frozen=True)
class QuestionRecord:
    id: str
    cutoff_date: str
    domain: str
    question: str
    features: dict[str, float]
    sources: tuple[str, ...] = ()
    labels: dict[str, int] | None = None
    evidence_groups: int = 0
    estimated_cost: float = 1.0
    data_access: float = 0.5

    @classmethod
    def from_dict(cls, value: dict) -> "QuestionRecord":
        missing = [key for key in ("id", "cutoff_date", "domain", "question", "features") if key not in value]
        if missing:
            raise ValueError(f"question record missing fields: {', '.join(missing)}")
        features = {key: float(value["features"].get(key, 0.0)) for key in FEATURES}
        labels = value.get("labels")
        if labels is not None:
            unknown = set(labels) - set(OUTCOMES)
            if unknown or any(int(labels[key]) not in (0, 1) for key in labels):
                raise ValueError("labels must contain binary Paper 3 outcomes only")
            labels = {key: int(val) for key, val in labels.items()}
        return cls(value["id"], value["cutoff_date"], value["domain"], value["question"],
                   features, tuple(value.get("sources", ())), labels,
                   int(value.get("evidence_groups", 0)), float(value.get("estimated_cost", 1.0)),
                   float(value.get("data_access", 0.5)))

    def to_dict(self) -> dict:
        result = asdict(self)
        result["sources"] = list(self.sources)
        return result


def load_jsonl(path: str | Path) -> list[QuestionRecord]:
    records = []
    for line_number, line in enumerate(Path(path).read_text().splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            records.append(QuestionRecord.from_dict(json.loads(line)))
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            raise ValueError(f"invalid question record at {path}:{line_number}: {exc}") from exc
    ids = [record.id for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("question IDs must be unique within a registry")
    return records


@dataclass(frozen=True)
class Forecast:
    question_id: str
    outcome: str
    probability: float
    model: str
    feature_snapshot: dict[str, float]


def forecast(record: QuestionRecord, outcome: str) -> Forecast:
    if outcome not in OUTCOMES:
        raise ValueError(f"unknown outcome: {outcome}")
    raise RuntimeError("CS outcome forecasts require an audited, out-of-time validated model")


def forecasts(records: Iterable[QuestionRecord]) -> list[Forecast]:
    return [forecast(record, outcome) for record in records for outcome in OUTCOMES]


def brier_score(labels: list[int], probabilities: list[float]) -> float:
    if not labels or len(labels) != len(probabilities):
        raise ValueError("labels and probabilities must be non-empty and aligned")
    return sum((probability - label) ** 2 for label, probability in zip(labels, probabilities)) / len(labels)


def auroc(labels: list[int], probabilities: list[float]) -> float | None:
    positives = [score for label, score in zip(labels, probabilities) if label == 1]
    negatives = [score for label, score in zip(labels, probabilities) if label == 0]
    if not positives or not negatives:
        return None
    wins = sum(1.0 if positive > negative else .5 if positive == negative else 0.0
               for positive in positives for negative in negatives)
    return wins / (len(positives) * len(negatives))


def auprc(labels: list[int], probabilities: list[float]) -> float | None:
    positives = sum(labels)
    if not positives:
        return None
    order = sorted(range(len(labels)), key=lambda index: probabilities[index], reverse=True)
    seen = 0
    area = 0.0
    previous_recall = 0.0
    for rank, index in enumerate(order, 1):
        if labels[index]:
            seen += 1
            recall = seen / positives
            precision = seen / rank
            area += (recall - previous_recall) * precision
            previous_recall = recall
    return area


def evaluate(records: list[QuestionRecord], outcome: str) -> dict:
    if outcome not in OUTCOMES:
        raise ValueError(f"unknown outcome: {outcome}")
    labels = [record.labels[outcome] for record in records
              if record.labels and outcome in record.labels]
    return {"outcome": outcome, "n": len(labels),
            "status": "no audited labels" if not labels else "no validated CS model",
            "auroc": None, "auprc": None, "brier": None,
            "positive_rate": sum(labels) / len(labels) if labels else None}


@dataclass(frozen=True)
class Opportunity:
    question_id: str
    scientific_significance: float
    uncertainty_reduction: float
    tractability: float
    reproducibility: float
    cost: float
    forecast_resolution: float
    forecast_revision: float
    score: float
    recommendation: str


def rank_opportunities(records: Iterable[QuestionRecord]) -> list[Opportunity]:
    raise RuntimeError("Direction rankings require validated CS forecasts and action outcomes")
