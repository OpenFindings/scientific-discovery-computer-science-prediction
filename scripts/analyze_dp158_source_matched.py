#!/usr/bin/env python3
"""Validate and compare the frozen independent scalar DP158 simulation."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

EXPECTED = {
    "q": 0.1,
    "T": 120,
    "sigma_0": 8.0,
    "sigma_min": 2.0,
    "C_0": 1.0,
    "budget_model": "paper_small_q",
    "output_dimension_used_for_adaptive_norm": 1,
    "trajectories_per_arm": 1000000,
    "rng_seeds": {"P": 260315, "Q": 260316},
}


def wilson_interval(successes: int, trials: int) -> list[float]:
    z = 1.959963984540054
    p = successes / trials
    denominator = 1.0 + z * z / trials
    center = (p + z * z / (2 * trials)) / denominator
    radius = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denominator
    return [center - radius, center + radius]


def analyze(raw: dict) -> dict:
    if raw["experiment_id"] != "EXP-DP158-SOURCE-MATCHED-EXPLORATORY-2026":
        raise ValueError("wrong experiment ID")
    parameters = raw["parameters"]
    for key, expected in EXPECTED.items():
        if parameters[key] != expected:
            raise ValueError(f"parameter mismatch for {key}: {parameters[key]!r}")
    expected_budget = 2000.0 * 0.5 * 0.1**2 * math.expm1(1.0 / 8.0**2)
    if not math.isclose(parameters["initial_budget"], expected_budget, rel_tol=1e-12):
        raise ValueError("budget does not match the source equation")

    published = raw["published_reference"]
    comparisons = {}
    for name in ("P", "Q"):
        arm = raw["arms"][name]
        if arm["seed"] != EXPECTED["rng_seeds"][name] or arm["trajectories"] != 1000000:
            raise ValueError(f"arm {name} seed or sample size mismatch")
        halted = round(arm["halt_probability"] * arm["trajectories"])
        if not math.isclose(arm["halt_probability"] + arm["censored_at_T_probability"], 1.0, abs_tol=1e-12):
            raise ValueError(f"arm {name} halt/censor accounting mismatch")
        comparisons[name] = {
            "halted": halted,
            "halt_probability": arm["halt_probability"],
            "halt_probability_95pct_wilson": wilson_interval(halted, arm["trajectories"]),
            "published_halt_probability": published[f"{name}_halt_probability"],
            "halt_probability_difference": arm["halt_probability"] - published[f"{name}_halt_probability"],
            "mean_active_steps": arm["mean_active_steps"],
            "published_mean_active_steps": published["mean_active_steps"],
            "mean_active_steps_difference": arm["mean_active_steps"] - published["mean_active_steps"],
            "plrv_mean": arm["plrv_mean"],
            "published_plrv_mean": published[f"{name}_plrv_mean"],
            "plrv_variance": arm["plrv_variance"],
            "published_plrv_variance": published[f"{name}_plrv_variance"],
            "max_empirical_cdf_difference": arm["max_empirical_cdf_difference"],
            "published_max_cdf_difference": published[f"{name}_max_cdf_difference"],
        }
    return {
        "experiment_id": raw["experiment_id"],
        "protocol": raw["protocol"],
        "source": "https://arxiv.org/html/2602.06756v2",
        "budget_formula": "q^2/2 * expm1(1/sigma_0^2)",
        "budget": parameters["initial_budget"],
        "comparisons": comparisons,
        "assessment": "Independent exploratory scalar simulation closely matches the reported Figure 12 stopping rates, steps, and PLRV moments. This is not author-code reproduction, a theorem verification, a production-accountant audit, or a general safety claim.",
        "unresolved": [
            "Appendix G.2 does not explicitly specify the zero-history C_1 convention; this implementation uses C_1=C_0. It also does not clarify scalar y_i^2 versus vector shorthand; this run uses one dimension.",
            "Single frozen Monte Carlo seed per arm; Wilson intervals quantify only halt-rate sampling noise.",
            "The result is post-source-audit exploratory because a prior incorrect exact-KL preregistration was withdrawn.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("results/dp158_filter_source_matched_q01/analysis.json"))
    parser.add_argument("--output", type=Path, default=Path("results/dp158_filter_source_matched_q01/independent_analysis.json"))
    args = parser.parse_args()
    result = analyze(json.loads(args.input.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
