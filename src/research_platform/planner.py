from __future__ import annotations

from dataclasses import dataclass
from .belief import expected_information_gain
from .models import Action


@dataclass(frozen=True)
class PlannerWeights:
    information_gain: float = 10.0
    novelty: float = 1.0
    tractability: float = 1.0
    cost: float = 1.0


def utility_breakdown(action: Action, beliefs: dict[str, float], weights: PlannerWeights,
                      observed_roots: set[str] | None = None) -> dict[str, float]:
    ig = expected_information_gain(action, beliefs)
    roots = set(observed_roots or ())
    novelty = (sum(root not in roots for root in action.provenance_roots) / len(action.provenance_roots)
               if action.provenance_roots else 0.0)
    components = {"information_gain": ig, "novelty": novelty,
                  "tractability": action.tractability, "cost": action.cost}
    components["utility"] = (weights.information_gain * ig + weights.novelty * novelty
                              + weights.tractability * action.tractability - weights.cost * action.cost)
    return components


def score(action: Action, beliefs: dict[str, float], weights: PlannerWeights,
          observed_roots: set[str] | None = None) -> float:
    return utility_breakdown(action, beliefs, weights, observed_roots)["utility"]


def rank_actions(actions: list[Action], beliefs: dict[str, float], weights: PlannerWeights,
                 observed_roots: set[str] | None = None) -> list[tuple[Action, float]]:
    return sorted(((action, score(action, beliefs, weights, observed_roots)) for action in actions),
                  key=lambda pair: (-pair[1], pair[0].id))
