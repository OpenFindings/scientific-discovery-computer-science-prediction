#!/usr/bin/env python3
"""Summarize the preregistered q=0.1 output-dimension sensitivity sweep."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


DIMENSIONS = (1, 2, 4, 8, 16)
Z_95 = 1.959963984540054


def wilson_interval(successes: int, trials: int) -> list[float]:
    if trials <= 0:
        raise ValueError("trials must be positive")
    p = successes / trials
    z2 = Z_95**2
    denominator = 1.0 + z2 / trials
    center = (p + z2 / (2.0 * trials)) / denominator
    radius = Z_95 * math.sqrt(p * (1.0 - p) / trials + z2 / (4.0 * trials**2)) / denominator
    return [center - radius, center + radius]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("results/dp158_filter_dimension_sensitivity"))
    parser.add_argument("--output", type=Path, default=Path("results/dp158_filter_dimension_sensitivity/summary.json"))
    args = parser.parse_args()

    arms_by_dimension: dict[int, dict[str, dict[str, object]]] = {}
    for dimension in DIMENSIONS:
        artifact = args.input / f"d{dimension}/analysis.json"
        result = json.loads(artifact.read_text())
        parameters = result["parameters"]
        expected_seeds = {"P": 261000 + 2 * dimension, "Q": 261001 + 2 * dimension}
        for name, actual, expected in (
            ("dimension", parameters["output_dimension_used_for_adaptive_norm"], dimension),
            ("trajectories", parameters["trajectories_per_arm"], 100000),
            ("q", parameters["q"], 0.1),
            ("T", parameters["T"], 120),
            ("sigma_0", parameters["sigma_0"], 8.0),
            ("sigma_min", parameters["sigma_min"], 2.0),
            ("C_0", parameters["C_0"], 1.0),
            ("seeds", parameters["rng_seeds"], expected_seeds),
        ):
            if actual != expected:
                raise SystemExit(f"{name} mismatch in {artifact}: {actual!r} != {expected!r}")
        if "budget_model" in parameters or not math.isclose(parameters["initial_budget"], 2000 * parameters["one_step_budget_cost_at_sigma_0"], rel_tol=1e-12):
            raise SystemExit(f"expected legacy exact-KL artifact in {artifact}")
        arms_by_dimension[dimension] = result["arms"]

    rows = []
    for dimension, arms in arms_by_dimension.items():
        row: dict[str, object] = {"dimension": dimension}
        for arm_name in ("P", "Q"):
            arm = arms[arm_name]
            n = int(arm["trajectories"])
            halted = round(float(arm["halt_probability"]) * n)
            row[arm_name] = {
                "halted": halted,
                "trajectories": n,
                "halt_probability": arm["halt_probability"],
                "halt_probability_95pct_wilson": wilson_interval(halted, n),
                "censored_at_T_probability": arm["censored_at_T_probability"],
                "mean_active_steps": arm["mean_active_steps"],
                "plrv_mean": arm["plrv_mean"],
                "plrv_variance": arm["plrv_variance"],
                "max_empirical_cdf_difference": arm["max_empirical_cdf_difference"],
            }
        rows.append(row)

    p_halts = [float(row["P"]["halt_probability"]) for row in rows]
    q_halts = [float(row["Q"]["halt_probability"]) for row in rows]
    p_steps = [float(row["P"]["mean_active_steps"]) for row in rows]
    q_steps = [float(row["Q"]["mean_active_steps"]) for row in rows]
    halt_range = max(max(p_halts) - min(p_halts), max(q_halts) - min(q_halts))
    step_range = max(max(p_steps) - min(p_steps), max(q_steps) - min(q_steps))
    result = {
        "experiment_id": "EXP-DP158-DIMENSION-SENSITIVITY-2026",
        "preregistration": "research/experiment_preregistration_dp158_dimension_sensitivity.md",
        "dimensions": list(DIMENSIONS),
        "trajectories_per_arm_dimension": 100000,
        "budget_model": "legacy_independent_exact_one_step_mixture_KL_not_paper_Budg",
        "primary_predeclared_decision": {
            "halt_probability_range_threshold": 0.01,
            "mean_active_step_range_threshold": 1.0,
            "halt_probability_range": halt_range,
            "mean_active_step_range": step_range,
            "dimension_is_material_under_rule": halt_range >= 0.01 or step_range >= 1.0,
        },
        "published_reference": {
            "P_halt_probability": 0.9886,
            "Q_halt_probability": 0.9880,
            "mean_active_steps": 113.1,
            "P_max_cdf_difference": 0.01247,
            "Q_max_cdf_difference": 0.01464,
        },
        "implementation_limitations": [
            "Correction after source audit: Appendix G.2 writes y_i^2 but does not clarify scalar output versus vector shorthand; the main algorithm permits vector output. This exact-KL vector sweep cannot establish that the paper omitted a needed parameter, and is not a paper reproduction.",
            "The legacy implementation uses exact one-step subsampled-Gaussian KL instead of the paper's explicit Budg(0,q,sigma,mu)=q^2/2*(exp(mu^2/sigma^2)-1). Its numerical comparison to Figure 12 is not source matched.",
            "Each arm/dimension uses one frozen Monte Carlo seed; Wilson intervals quantify only binomial halt-rate noise, not all implementation or model uncertainty.",
            "This is a simulation reproducibility/sensitivity observation, not a production accountant audit or a general DP failure.",
        ],
        "dimension_results": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
