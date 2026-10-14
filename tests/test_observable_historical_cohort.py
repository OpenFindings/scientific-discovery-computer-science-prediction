import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("observable_selector", ROOT / "scripts/select_observable_historical_cohort.py")
SELECTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SELECTOR)


class ObservableCohortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame = [json.loads(line) for line in (ROOT / "data/historical_cs_year_topic_frame.jsonl").read_text().splitlines()]
        cls.old = [json.loads(line) for line in (ROOT / "data/historical_cs_blind_cohort_20.jsonl").read_text().splitlines()]

    def test_source_only_selection_reproduces_frozen_cohort(self):
        rows, profile = SELECTOR.select(self.frame, self.old)
        saved = [json.loads(line) for line in (ROOT / "data/historical_cs_observable_cohort_16.jsonl").read_text().splitlines()]
        self.assertEqual(rows, saved)
        self.assertEqual(len(rows), 16)
        self.assertEqual(len({r["arxiv_id"] for r in rows}), 16)
        self.assertTrue({r["arxiv_id"] for r in rows}.isdisjoint({r["arxiv_id"] for r in self.old}))
        self.assertFalse(profile["selection_uses_future_outcomes"])
        self.assertTrue(all(r["outcome_status"] == "sealed_not_searched" for r in rows))

    def test_rejects_future_revision_in_eligible_pool(self):
        row = next(r for r in self.frame if r["sampling_topic"] == "algorithms_complexity" and r["as_of"].startswith("2017") and "complexity" in r["title"].lower())
        bad = dict(row, updated="2026-01-01T00:00:00Z")
        with self.assertRaises(ValueError):
            SELECTOR.select([bad], [])


if __name__ == "__main__":
    unittest.main()
