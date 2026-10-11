from __future__ import annotations

from dataclasses import dataclass
from .belief import expected_information_gain
from .models import Action


@dataclass(frozen=True)
class PlannerWeights:
    information_gain: float = 1.0
    novelty: float = 0.0
    tractability: float = 1.0
    cost: float = 1.0


def score(action: Action, beliefs: dict[str, float], weights: PlannerWeights) -> float:
    ig = expected_information_gain(action, beliefs)
    return (weights.information_gain * ig + weights.novelty * 0.0
            + weights.tractability * action.tractability - weights.cost * action.cost)


def rank_actions(actions: list[Action], beliefs: dict[str, float], weights: PlannerWeights) -> list[tuple[Action, float]]:
    return sorted(((action, score(action, beliefs, weights)) for action in actions),
                  key=lambda pair: (-pair[1], pair[0].id))

