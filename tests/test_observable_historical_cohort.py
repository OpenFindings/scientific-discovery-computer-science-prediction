import importlib.util
import json
from pathlib import Path
import unittest
from datetime import date


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

    def test_trajectory_does_not_promote_near_match_to_resolution(self):
        trajectory = json.loads((ROOT / "reports/historical_evidence_trajectory_round1.json").read_text())
        screens = [json.loads((ROOT / path).read_text()) for path in trajectory["source_screens"]]
        self.assertTrue(all(not screen["future_evidence_searched_for_these_questions"] for screen in screens))
        locked = {row["versioned_id"]: row for screen in screens for row in screen["rows"] if row["question_status"] == "eligible_source_open"}
        self.assertEqual(set(locked), {row["versioned_id"] for row in trajectory["rows"]})
        self.assertEqual(trajectory["counts"]["source_screened"], 10)
        self.assertEqual(trajectory["counts"]["eligible_questions"], len(locked))
        self.assertEqual(trajectory["counts"]["future_audited_questions"], len(trajectory["rows"]))
        self.assertEqual(trajectory["counts"]["direct_resolution_supported"], 0)
        self.assertEqual(trajectory["counts"]["partial_progress_supported"], sum(row["dimensions"]["partial_progress"] == "supported" for row in trajectory["rows"]))
        for row in trajectory["rows"]:
            self.assertEqual(row["question"], locked[row["versioned_id"]]["candidate_question"])
            self.assertTrue(row["unadjudicated_direct_outcome"])
            self.assertEqual(row["dimensions"]["direct_scientific_resolution"], "not_observed_after_bounded_search")
            self.assertEqual(len(row["dimensions"]), 7)
            for evidence in row["evidence"]:
                observed = date.fromisoformat(evidence["first_public_date"])
                self.assertGreater(observed, date.fromisoformat(row["cutoff"][:10]))
                self.assertLessEqual(observed, date.fromisoformat(row["followup_end"][:10]))

    def test_original_blind_cohort_untouched(self):
        trajectory = json.loads((ROOT / "reports/historical_evidence_trajectory_round1.json").read_text())
        original_ids = {row["arxiv_id"] for row in self.old}
        self.assertTrue(original_ids.isdisjoint({row["versioned_id"].split("v")[0] for row in trajectory["rows"]}))


if __name__ == "__main__":
    unittest.main()
