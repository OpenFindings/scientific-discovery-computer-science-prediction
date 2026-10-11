from __future__ import annotations

from math import isclose
from collections import defaultdict
from .models import Hypothesis, Action, Evidence


def normalize(priors: dict[str, float]) -> dict[str, float]:
    total = sum(priors.values())
    if total <= 0:
        raise ValueError("belief mass must be positive")
    return {key: value / total for key, value in priors.items()}


def update_beliefs(
    beliefs: dict[str, float], action: Action, evidence: Evidence, *, floor: float = 1e-12
) -> dict[str, float]:
    """Bayesian update using declared likelihoods; no likelihood is guessed implicitly."""
    outcome = str(evidence.observation.get("outcome"))
    likelihoods = action.expected_outcomes.get(outcome)
    if likelihoods is None:
        raise ValueError(f"action {action.id} has no declared likelihood for {outcome!r}")
    weighted = {hypothesis: max(floor, beliefs.get(hypothesis, 0.0)) * likelihoods.get(hypothesis, floor)
                for hypothesis in beliefs}
    return normalize(weighted)


def entropy(beliefs: dict[str, float]) -> float:
    from math import log
    return -sum(p * log(p) for p in beliefs.values() if p > 0)


def expected_information_gain(action: Action, beliefs: dict[str, float]) -> float:
    """Expected entropy reduction under the action's declared outcome model."""
    outcomes: dict[str, float] = defaultdict(float)
    for outcome, likelihoods in action.expected_outcomes.items():
        outcomes[outcome] = sum(beliefs.get(h, 0.0) * p for h, p in likelihoods.items())
    base = entropy(beliefs)
    posterior_entropy = 0.0
    for outcome, probability in outcomes.items():
        if probability <= 0:
            continue
        posterior = normalize({h: beliefs.get(h, 0.0) * likelihoods.get(h, 1e-12)
                               for h in beliefs} ) if (likelihoods := action.expected_outcomes[outcome]) else beliefs
        posterior_entropy += probability * entropy(posterior)
    return max(0.0, base - posterior_entropy)
