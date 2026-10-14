"""Numerical and source-formula guardrails for the independent DP158 simulator."""

import math
import json
import unittest
from pathlib import Path

import numpy as np

from scripts.reproduce_dp158_q01_filter import (
    Q,
    build_kl_lookup,
    inverse_paper_small_q_budget,
    log_likelihood_ratio,
    paper_small_q_budget,
    run_arm,
)
from scripts.analyze_dp158_source_matched import analyze


class Dp158FormulaTests(unittest.TestCase):
    def test_paper_budget_matches_figure_12_rounding(self):
        cost = float(paper_small_q_budget(1.0 / 8.0))
        self.assertAlmostEqual(cost, Q * Q * math.expm1(1.0 / 64.0) / 2.0)
        self.assertAlmostEqual(2000 * cost, 0.1575, delta=0.0001)

    def test_paper_budget_inverse(self):
        r = np.array([0.0, 0.125, 0.25, 0.5])
        np.testing.assert_allclose(inverse_paper_small_q_budget(paper_small_q_budget(r)), r, atol=1e-14)
        np.testing.assert_allclose(inverse_paper_small_q_budget(paper_small_q_budget(r, 0.5), 0.5), r, atol=1e-14)

    def test_mixture_likelihood_at_zero_signal(self):
        z = np.array([-3.0, 0.0, 2.0])
        np.testing.assert_allclose(log_likelihood_ratio(z, np.zeros_like(z)), np.zeros_like(z), atol=1e-15)

    def test_exact_kl_is_distinct_from_paper_approximation(self):
        grid_r, grid_kl, _ = build_kl_lookup()
        exact_cost = float(np.interp(0.5, grid_r, grid_kl))
        paper_cost = float(paper_small_q_budget(0.5))
        self.assertGreater(paper_cost, exact_cost)
        self.assertGreater(exact_cost, 0)
        grid_r_05, grid_kl_05, _ = build_kl_lookup(0.5)
        self.assertGreater(float(np.interp(0.5, grid_r_05, grid_kl_05)), exact_cost)

    def test_scalar_short_run_is_deterministic(self):
        grid_r, grid_kl, _ = build_kl_lookup()
        budget = 2000 * float(paper_small_q_budget(0.125))
        first = run_arm("Q", 12345, 1000, 1, budget, grid_r, grid_kl, "paper_small_q")
        second = run_arm("Q", 12345, 1000, 1, budget, grid_r, grid_kl, "paper_small_q")
        self.assertEqual(first, second)
        self.assertLessEqual(first["halt_probability"], 1)
        self.assertGreaterEqual(first["halt_probability"], 0)
        self.assertLessEqual(first["mean_active_steps"], 120)

    def test_independent_analysis_rejects_wrong_budget_model(self):
        artifact = Path(__file__).resolve().parents[1] / "results/dp158_filter_source_matched_q01/analysis.json"
        raw = json.loads(artifact.read_text())
        self.assertEqual(analyze(raw)["comparisons"]["P"]["halted"], 988712)
        raw["parameters"]["budget_model"] = "exact_kl"
        with self.assertRaisesRegex(ValueError, "budget_model"):
            analyze(raw)


if __name__ == "__main__":
    unittest.main()
