"""Theorem-formula and pre-release-stop guardrails for the RDP reference."""

import math
import unittest

import numpy as np

from research_platform.rdp_filter_reference import FixedOrderRdpFilter, revealed_coin_rdp_upper


class RdpFilterReferenceTests(unittest.TestCase):
    def test_forward_exact_order_two_is_below_revealed_coin_bound(self):
        for q in (0.01, 0.1, 0.5, 0.95):
            for r in (0.125, 0.25, 0.5):
                forward_exact = math.log1p(q * q * math.expm1(r * r))
                self.assertLessEqual(forward_exact, revealed_coin_rdp_upper(2.0, q, r))

    def test_edge_cases_and_invalid_inputs(self):
        self.assertEqual(revealed_coin_rdp_upper(2.0, 0.0, 0.5), 0.0)
        self.assertEqual(revealed_coin_rdp_upper(2.0, 0.5, 0.0), 0.0)
        self.assertAlmostEqual(revealed_coin_rdp_upper(2.0, 1.0, 0.5), 0.25)
        for alpha, q, r in ((1.0, 0.1, 0.5), (2.0, -0.1, 0.5), (2.0, 0.1, -0.1)):
            with self.assertRaises(ValueError):
                revealed_coin_rdp_upper(alpha, q, r)

    def test_reverse_order_two_quadrature_is_below_bound(self):
        nodes, weights = np.polynomial.hermite.hermgauss(96)
        z = math.sqrt(2) * nodes
        normal_weights = weights / math.sqrt(math.pi)
        for q in (0.01, 0.1, 0.5, 0.95):
            for r in (0.125, 0.25, 0.5):
                mixture_ratio = 1 - q + q * np.exp(r * z - r * r / 2)
                reverse_d2 = math.log(float(np.sum(normal_weights / mixture_ratio)))
                self.assertLessEqual(reverse_d2, revealed_coin_rdp_upper(2.0, q, r) + 1e-13)

    def test_halts_before_budget_exceeding_release(self):
        account = FixedOrderRdpFilter(alpha=2.0, budget=0.1)
        accepted = 0
        for step in range(100):
            # Predictable adaptive schedule; costs depend on the previous step.
            q = 0.1 + 0.01 * (step % 3)
            r = 0.2 + 0.02 * accepted
            if not account.try_release(q, r):
                break
            accepted += 1
            self.assertLessEqual(account.spent, account.budget)
        self.assertGreater(accepted, 0)
        self.assertLess(accepted, 100)
        self.assertEqual(len(account.charges), accepted)


if __name__ == "__main__":
    unittest.main()
