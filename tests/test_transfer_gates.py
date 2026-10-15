import unittest

from research_platform.historical import snapshot_report
from research_platform.opportunity import QuestionRecord, evaluate, forecast, rank_opportunities


class TransferGateTests(unittest.TestCase):
    def setUp(self):
        self.record = QuestionRecord(
            id="q1", cutoff_date="2020-01-01", domain="cs",
            question="Will this hypothesis survive a later test?", features={},
            labels={"attention": 1},
        )

    def test_no_implicit_forecast_or_rank(self):
        with self.assertRaisesRegex(RuntimeError, "validated model"):
            forecast(self.record, "attention")
        with self.assertRaisesRegex(RuntimeError, "action outcomes"):
            rank_opportunities([self.record])

    def test_labels_alone_do_not_create_model_metrics(self):
        result = evaluate([self.record], "attention")
        self.assertEqual(result["status"], "no validated CS model")
        self.assertIsNone(result["auroc"])
        report = snapshot_report([self.record], ["2020-12-31"])
        self.assertIsNone(report["snapshots"][0]["outcomes"]["attention"]["auroc"])


if __name__ == "__main__":
    unittest.main()
