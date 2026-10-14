#!/usr/bin/env python3
"""Independent scalar Monte Carlo test of the q=0.1 DP158 filter figure."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


Q = 0.1
T = 120
SIGMA_0 = 8.0
SIGMA_MIN = 2.0
C_0 = 1.0
TRAJECTORIES = 1_000_000
SEEDS = {"P": 260213, "Q": 260214}
GH_NODES = 48
KL_GRID_SIZE = 32_769
KL_GRID_MAX = 0.5


def log_likelihood_ratio(z: np.ndarray, signal_to_noise: np.ndarray) -> np.ndarray:
    """Log dP/dQ for Q=N(0,1), P=(1-q)N(0,1)+qN(r,1)."""
    return np.logaddexp(
        math.log1p(-Q),
        math.log(Q) + signal_to_noise * z - 0.5 * signal_to_noise**2,
    )


def build_kl_lookup() -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    """Tabulate exact mixture KL by Gauss-Hermite integration over N(0,1)."""
    nodes, weights = np.polynomial.hermite.hermgauss(GH_NODES)
    standard_normal_nodes = math.sqrt(2.0) * nodes
    standard_normal_weights = weights / math.sqrt(math.pi)
    r_grid = np.linspace(0.0, KL_GRID_MAX, KL_GRID_SIZE, dtype=np.float64)
    kl_grid = np.empty_like(r_grid)
    log_q = math.log(Q)
    log_not_q = math.log1p(-Q)

    for start in range(0, len(r_grid), 2048):
        r = r_grid[start : start + 2048, None]
        base_z = np.broadcast_to(standard_normal_nodes, (len(r), GH_NODES))
        under_q = np.logaddexp(log_not_q, log_q + r * base_z - 0.5 * r**2)
        under_p = np.logaddexp(log_not_q, log_q + r * (base_z + r) - 0.5 * r**2)
        kl_grid[start : start + len(r)] = (1.0 - Q) * (under_q @ standard_normal_weights) + Q * (
            under_p @ standard_normal_weights
        )
    kl_grid[0] = 0.0
    if np.any(np.diff(kl_grid) <= 0):
        raise RuntimeError("Gauss-Hermite KL lookup is not strictly increasing")
    metadata = {
        "quadrature": "Gauss-Hermite for standard normal expectation",
        "gauss_hermite_nodes": GH_NODES,
        "kl_grid_size": KL_GRID_SIZE,
        "kl_grid_signal_to_noise_max": KL_GRID_MAX,
        "inverse_kl": "linear interpolation of the frozen monotone lookup table",
    }
    return r_grid, kl_grid, metadata


def paper_small_q_budget(r: np.ndarray | float) -> np.ndarray | float:
    """Budg(0,q,sigma,mu) = q²/2 * (exp((mu/sigma)²)-1)."""
    return 0.5 * Q**2 * np.expm1(np.asarray(r) ** 2)


def inverse_paper_small_q_budget(cost: np.ndarray) -> np.ndarray:
    return np.sqrt(np.log1p(2.0 * cost / Q**2))


def gaussian_cdf(values: np.ndarray, mean: float, variance: float) -> np.ndarray:
    z = (values - mean) / math.sqrt(variance)
    return np.fromiter(
        (0.5 * math.erfc(-float(value) / math.sqrt(2.0)) for value in z),
        dtype=np.float64,
        count=len(z),
    )


def run_arm(
    arm: str,
    seed: int,
    n: int,
    dimension: int,
    budget: float,
    r_grid: np.ndarray,
    kl_grid: np.ndarray,
    budget_model: str,
) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    history_sq = np.zeros(n, dtype=np.float64)
    remaining = np.full(n, budget, dtype=np.float64)
    cumulative_plrv = np.zeros(n, dtype=np.float64)
    active = np.ones(n, dtype=bool)
    active_steps = np.zeros(n, dtype=np.uint16)

    for step in range(T):
        indices = np.flatnonzero(active)
        if not len(indices):
            break
        hist = history_sq[indices]
        root_hist = np.sqrt(hist)
        if step == 0:
            sigma = np.full(len(indices), SIGMA_0, dtype=np.float64)
            clip = np.full(len(indices), C_0, dtype=np.float64)
        else:
            sigma = np.clip(SIGMA_0 / root_hist, SIGMA_MIN, SIGMA_0)
            clip = C_0 / root_hist
        full_r = 1.0 / sigma
        if budget_model == "paper_small_q":
            full_cost = paper_small_q_budget(full_r)
        else:
            full_cost = np.interp(full_r, r_grid, kl_grid)
        budget_left = remaining[indices]
        partial = budget_left < full_cost
        if budget_model == "paper_small_q":
            capped_r = np.minimum(full_r, inverse_paper_small_q_budget(np.maximum(budget_left, 0.0)))
        else:
            capped_r = np.minimum(full_r, np.interp(np.maximum(budget_left, 0.0), kl_grid, r_grid))

        noise = rng.standard_normal(len(indices))
        if arm == "P":
            included = rng.random(len(indices)) < Q
            observed_standardized = noise + included * capped_r
        else:
            observed_standardized = noise

        step_plrv = log_likelihood_ratio(observed_standardized, capped_r)
        cumulative_plrv[indices] += step_plrv
        squared_standard_normal_norm = observed_standardized**2
        if dimension > 1:
            squared_standard_normal_norm += rng.chisquare(dimension - 1, size=len(indices))
        output_norm_squared = (sigma * clip) ** 2 * squared_standard_normal_norm
        history_sq[indices] += output_norm_squared
        active_steps[indices] += 1
        remaining[indices] = np.maximum(0.0, budget_left - full_cost)
        active[indices[partial]] = False

    halted = ~active
    values = cumulative_plrv
    expected_mean = budget if arm == "P" else -budget
    expected_variance = 2.0 * budget
    order = np.argsort(values)
    sorted_values = values[order]
    empirical_cdf = np.arange(1, n + 1, dtype=np.float64) / n
    gaussian = gaussian_cdf(sorted_values, expected_mean, expected_variance)
    max_cdf_difference = float(
        max(
            np.max(np.abs(empirical_cdf - gaussian)),
            np.max(np.abs(empirical_cdf - 1.0 / n - gaussian)),
        )
    )
    return {
        "arm": arm,
        "seed": seed,
        "output_dimension": dimension,
        "trajectories": n,
        "halt_probability": float(np.mean(halted)),
        "censored_at_T_probability": float(np.mean(active)),
        "mean_active_steps": float(np.mean(active_steps)),
        "plrv_mean": float(np.mean(values)),
        "plrv_variance": float(np.var(values)),
        "target_gaussian_mean": expected_mean,
        "target_gaussian_variance": expected_variance,
        "max_empirical_cdf_difference": max_cdf_difference,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results/dp158_filter_reproduction_q01/analysis.json"))
    parser.add_argument("--trajectories", type=int, default=TRAJECTORIES)
    parser.add_argument("--dimension", type=int, default=1)
    parser.add_argument("--seed-p", type=int, default=SEEDS["P"])
    parser.add_argument("--seed-q", type=int, default=SEEDS["Q"])
    parser.add_argument("--budget-model", choices=("paper_small_q", "exact_kl"), default="paper_small_q")
    args = parser.parse_args()
    if args.trajectories < 1000:
        raise SystemExit("--trajectories must be at least 1000")
    if args.dimension < 1 or args.dimension > 1024:
        raise SystemExit("--dimension must be in [1, 1024]")

    r_grid, kl_grid, numerical = build_kl_lookup()
    one_step_cost = float(np.interp(1.0 / SIGMA_0, r_grid, kl_grid))
    paper_one_step_cost = float(paper_small_q_budget(1.0 / SIGMA_0))
    budget = 2000.0 * (paper_one_step_cost if args.budget_model == "paper_small_q" else one_step_cost)
    seeds = {"P": args.seed_p, "Q": args.seed_q}
    arms = {
        arm: run_arm(arm, seeds[arm], args.trajectories, args.dimension, budget, r_grid, kl_grid, args.budget_model)
        for arm in ("P", "Q")
    }
    result = {
        "experiment_id": "EXP-DP158-SOURCE-MATCHED-EXPLORATORY-2026" if args.budget_model == "paper_small_q" else "EXP-DP158-EXACT-KL-VARIANT-2026",
        "protocol": "research/protocol_dp158_source_matched_exploratory.md" if args.budget_model == "paper_small_q" else "research/experiment_preregistration_dp158_dimension_sensitivity.md",
        "source": "arXiv:2602.06756v2 Appendix G.2 / Figure 12 / Table 3",
        "implementation_status": "independent_reference_implementation_not_author_code",
        "parameters": {
            "q": Q,
            "T": T,
            "sigma_0": SIGMA_0,
            "sigma_min": SIGMA_MIN,
            "C_0": C_0,
            "output_dimension_used_for_adaptive_norm": args.dimension,
            "initial_budget": budget,
            "budget_model": args.budget_model,
            "one_step_budget_cost_at_sigma_0": paper_one_step_cost if args.budget_model == "paper_small_q" else one_step_cost,
            "exact_kl_one_step_at_sigma_0_for_diagnostics": one_step_cost,
            "trajectories_per_arm": args.trajectories,
            "numpy_version": np.__version__,
            "rng": "NumPy PCG64",
            "rng_seeds": seeds,
            **numerical,
        },
        "published_reference": {
            "initial_budget_approx": 0.1575,
            "P_halt_probability": 0.9886,
            "Q_halt_probability": 0.9880,
            "mean_active_steps": 113.1,
            "P_plrv_mean": 0.1526,
            "P_plrv_variance": 0.314,
            "Q_plrv_mean": -0.1494,
            "Q_plrv_variance": 0.2912,
            "P_max_cdf_difference": 0.01247,
            "Q_max_cdf_difference": 0.01464,
        },
        "arms": arms,
        "interpretation": "Independent one-dimensional instantiation, not author code. Appendix G.2 writes y_i^2 but does not clarify scalar output versus vector shorthand or fully specify the zero-history clipping convention. Not a production-accountant audit or proof of a DP failure.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
