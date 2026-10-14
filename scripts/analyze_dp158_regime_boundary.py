#!/usr/bin/env python3
"""Validate the frozen DP158 boundary sweep and its simultaneous DKW contrasts."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


DESIGN = (("q010", 0.1, 260500, 260501),
          ("q019", 0.19, 260502, 260503),
          ("q030", 0.3, 260504, 260505),
          ("q050", 0.5, 260506, 260507))
N = 1_000_000
ALPHA_FAMILY = 0.05
P_SIDES = 8
DKW_RADIUS = math.sqrt(math.log(2 * P_SIDES / ALPHA_FAMILY) / (2 * N))


def analyze(root: Path) -> dict:
    rows = []
    for key, q, seed_p, seed_q in DESIGN:
        path = root / key / "analysis.json"
        raw = json.loads(path.read_text())
        if raw["experiment_id"] != "EXP-DP158-REGIME-BOUNDARY-2026":
            raise ValueError(f"wrong experiment ID in {path}")
        p = raw["parameters"]
        for name, expected in (("q", q), ("T", 120), ("sigma_0", 8.0),
                               ("sigma_min", 2.0), ("C_0", 1.0),
                               ("budget_model", "paper_small_q"),
                               ("output_dimension_used_for_adaptive_norm", 1),
                               ("trajectories_per_arm", N),
                               ("rng_seeds", {"P": seed_p, "Q": seed_q})):
            if p[name] != expected:
                raise ValueError(f"{name} mismatch in {path}")
        expected_budget = 2000 * .5 * q * q * math.expm1(1 / 8**2)
        if not math.isclose(p["initial_budget"], expected_budget, rel_tol=1e-12):
            raise ValueError(f"budget formula mismatch in {path}")
        arms = {}
        for arm_name in ("P", "Q"):
            a = raw["arms"][arm_name]
            if a["trajectories"] != N or a["seed"] != p["rng_seeds"][arm_name]:
                raise ValueError(f"arm size/seed mismatch in {path}")
            arms[arm_name] = {
                "halt_probability": a["halt_probability"],
                "mean_active_steps": a["mean_active_steps"],
                "plrv_mean": a["plrv_mean"],
                "plrv_variance": a["plrv_variance"],
                "max_empirical_cdf_difference": a["max_empirical_cdf_difference"],
            }
        rows.append({"q": q, "budget": p["initial_budget"], "arms": arms,
                     "max_cdf_discrepancy": max(a["max_empirical_cdf_difference"] for a in arms.values())})
    baseline = rows[0]["max_cdf_discrepancy"]
    for index, row in enumerate(rows):
        delta = row["max_cdf_discrepancy"] - baseline
        radius = 0.0 if index == 0 else 2 * DKW_RADIUS
        row["contrast_vs_q010"] = {
            "observed_difference": delta,
            "simultaneous_95pct_lower": delta - radius,
            "simultaneous_95pct_upper": delta + radius,
            "material_under_predeclared_rule": delta - radius > 0.01,
        }
    return {
        "experiment_id": "EXP-DP158-REGIME-BOUNDARY-2026",
        "protocol": "research/protocol_dp158_regime_boundary_next.md",
        "source": "https://arxiv.org/html/2602.06756v2",
        "sample_size_per_arm_q": N,
        "simultaneous_dkw": {"familywise_alpha": ALPHA_FAMILY, "number_of_ecdfs": P_SIDES,
                             "per_ecdf_radius": DKW_RADIUS,
                             "contrast_radius": 2 * DKW_RADIUS},
        "rows": rows,
        "decision": "The q=0.19, q=0.3 and q=0.5 one-dimensional empirical Gaussian-CDF discrepancy increases exceed the predeclared 0.01 materiality threshold after simultaneous Monte Carlo uncertainty (q=0.19 narrowly). This is a finite-q numerical limitation already anticipated by the paper, not a theorem counterexample, formal q cutoff, production vulnerability, or matched-privacy accountant comparison.",
        "limitations": [
            "The published theorem is asymptotic near q=0 or q=1 and makes no exact finite-q=0.3/0.5 guarantee.",
            "Only one frozen Monte Carlo seed per arm/q; DKW controls empirical-CDF sampling noise, not model or code uncertainty.",
            "The zero-history clipping and scalar-versus-vector conventions remain unverified against author code.",
            "The RDP reference filter was unit-tested separately but not compared here at a matched (epsilon,delta) guarantee.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("results/dp158_regime_boundary"))
    parser.add_argument("--output", type=Path, default=Path("results/dp158_regime_boundary/summary.json"))
    args = parser.parse_args()
    result = analyze(args.input)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
