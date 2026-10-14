"""Guardrails for frozen equal-CPU SQLancer++ study setup and receipts."""

import tempfile
import unittest
from pathlib import Path

from scripts.run_sqlancerpp_equal_cpu_campaign import BUDGET_USEC, SEEDS, derive_arm, frozen_orders, parse_receipt
from scripts.analyze_sqlancerpp_equal_cpu_campaign import analyze, exact_sign_test


class EqualCpuRunnerTests(unittest.TestCase):
    def test_balanced_order_is_frozen(self):
        orders = frozen_orders()
        self.assertEqual(set(orders), set(SEEDS))
        self.assertEqual([orders[seed][0] for seed in SEEDS],
                         ["feedback_off", "feedback_off", "feedback_on", "feedback_off", "feedback_on"])
        self.assertEqual(sum(order[0] == "feedback_on" for order in orders.values()), 2)

    def test_receipt_checks_cpu_delta(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "stop_receipt.txt"
            path.write_text(f"start_cpu_usec=100\nend_cpu_usec={BUDGET_USEC + 150}\nused_cpu_usec={BUDGET_USEC + 50}\nbudget_usec={BUDGET_USEC}\nstop_reason=cpu_budget\nchild_status=143\n")
            self.assertEqual(int(parse_receipt(path)["used_cpu_usec"]), BUDGET_USEC + 50)
            path.write_text(path.read_text().replace(f"used_cpu_usec={BUDGET_USEC + 50}", "used_cpu_usec=10"))
            with self.assertRaisesRegex(ValueError, "inconsistent"):
                parse_receipt(path)

    def test_candidate_log_is_database_log_not_rolling_trace(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            logs = run_dir / "logs/general"
            logs.mkdir(parents=True)
            (logs / "db0-cur.log").write_text("-- Database version: 3.40.0\n")
            (logs / "db0.log").write_text("AssertionError: discrepancy\n")
            (run_dir / "stdout.log").write_text("Success rate for query pairs: 0.5\n" * 8)
            (run_dir / "stderr.log").write_text("")
            (run_dir / "stop_receipt.txt").write_text(
                f"start_cpu_usec=100\nend_cpu_usec={BUDGET_USEC + 100}\n"
                f"used_cpu_usec={BUDGET_USEC}\nbudget_usec={BUDGET_USEC}\n"
                "stop_reason=cpu_budget\nchild_status=143\n"
            )
            arm = derive_arm(run_dir, "feedback_off", 0, 4.8)
            self.assertEqual(arm["candidate_error_logs"], ["logs/general/db0.log"])
            self.assertTrue(arm["counter_complete"])

    def test_independent_analysis_reparses_frozen_study(self):
        root = Path(__file__).resolve().parents[1] / "results/sqlancerpp_feedback_equal_cpu_4131_4135"
        result = analyze(root)
        self.assertEqual(result["complete_pairs"], 5)
        self.assertEqual(result["secondary_successful_pair_differences_on_minus_off"], [25, 51, 228, 393, -15])
        self.assertEqual(result["bug_candidate_signals"], [])
        self.assertEqual(result["primary_confirmed_distinct_norec_bugs"], 0)
        self.assertEqual(exact_sign_test([25, 51, 228, 393, -15])["two_sided_p"], 0.375)


if __name__ == "__main__":
    unittest.main()
