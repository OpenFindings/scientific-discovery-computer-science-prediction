import gzip
import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_historical_cs_frame import audit
from scripts.select_historical_blind_cohort import EXCLUDED_PILOTS, select


class HistoricalFrameTests(unittest.TestCase):
    def test_repository_frame_is_year_end_safe(self):
        root = Path(__file__).resolve().parents[1]
        report = json.loads((root / "reports/broad_cs_historical_audit.json").read_text())
        frame = [json.loads(line) for line in (root / "data/historical_cs_year_topic_frame.jsonl").read_text().splitlines()]
        self.assertEqual(len(frame), report["sampling"]["selected_topic_year_rows"])
        self.assertEqual(len({row["arxiv_id"] for row in frame}), report["sampling"]["unique_arxiv_ids_selected"])
        self.assertTrue(all(row["updated"] <= row["as_of"] for row in frame))
        self.assertTrue(all(int(row["as_of"][:4]) + 3 == int(row["three_year_followup_end"][:4]) for row in frame))
        selected_per_cell = {}
        for row in frame:
            cell = (row["as_of"], row["sampling_topic"])
            selected_per_cell[cell] = selected_per_cell.get(cell, 0) + 1
        self.assertTrue(all(n <= 5 for n in selected_per_cell.values()))
        candidates = [json.loads(line) for line in (root / "research/historical_question_candidates.jsonl").read_text().splitlines()]
        selected_ids = {row["versioned_id"] for row in frame}
        self.assertEqual(len(candidates), 3)
        self.assertTrue(all(row["source_paper_id"] in selected_ids for row in candidates))
        self.assertTrue(all(row["outcome_label"] == "unadjudicated" for row in candidates))
        adjudication = json.loads((root / "reports/historical_source_adjudication.json").read_text())
        self.assertEqual({row["question_id"] for row in adjudication["rows"]},
                         {row["question_id"] for row in candidates})
        self.assertEqual(adjudication["counts"]["source_fulltexts_reviewed"], 3)
        self.assertEqual(adjudication["counts"]["direct_three_year_followup_resolutions_adjudicated"], 0)
        pilot = json.loads((root / "reports/historical_outcome_adjudication.json").read_text())
        self.assertIn(pilot["source"]["versioned_id"], selected_ids)
        self.assertLess(pilot["source"]["version_date"], pilot["cutoff"][:10])
        self.assertGreater(pilot["later_primary_evidence"]["first_publication"], pilot["cutoff"][:10])
        self.assertLessEqual(pilot["later_primary_evidence"]["first_publication"], "2024-12-31")
        self.assertEqual(pilot["adjudication"]["question_resolution"], "not_established")
        self.assertIn("not_forecast_validation", pilot["status"])
        blind = [json.loads(line) for line in (root / "data/historical_cs_blind_cohort_20.jsonl").read_text().splitlines()]
        selected_again, protocol = select(frame)
        self.assertEqual(blind, selected_again)
        self.assertEqual(len(blind), 20)
        self.assertEqual(len({row["arxiv_id"] for row in blind}), 20)
        self.assertTrue(all(row["arxiv_id"] not in EXCLUDED_PILOTS for row in blind))
        self.assertTrue(all(row["future_outcome_status"] == "sealed_not_searched" for row in blind))
        self.assertEqual(protocol["selected_rows"], 20)

    def test_excludes_future_revisions_and_preserves_three_year_window(self):
        rows = [
        {"arxiv_id": "a", "versioned_id": "av1", "title": "A", "published": "2017-01-01T00:00:00Z",
         "updated": "2017-02-01T00:00:00Z", "abstract_url": "https://example.org/a", "pdf_url": "https://example.org/a.pdf",
         "screen_matches": [{"topic": "security_privacy"}]},
        {"arxiv_id": "b", "versioned_id": "bv2", "title": "B", "published": "2017-01-01T00:00:00Z",
         "updated": "2018-01-01T00:00:00Z", "abstract_url": "https://example.org/b", "pdf_url": "https://example.org/b.pdf",
         "screen_matches": [{"topic": "security_privacy"}]},
        {"arxiv_id": "c", "versioned_id": "cv1", "title": "C", "published": "2023-01-01T00:00:00Z",
         "updated": "2023-01-01T00:00:00Z", "abstract_url": "https://example.org/c", "pdf_url": "https://example.org/c.pdf",
         "screen_matches": [{"topic": "security_privacy"}]},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.jsonl.gz"
            with gzip.open(path, "wt", encoding="utf-8") as stream:
                for row in rows:
                    stream.write(json.dumps(row) + "\n")
            report, frame = audit(path)
            self.assertEqual(report["records_scanned"], 3)
            self.assertEqual(report["historical_lexical_candidates"], 2)
            self.assertEqual(report["later_revised_latest_metadata_excluded"], 1)
            self.assertEqual([row["arxiv_id"] for row in frame], ["a"])
            self.assertEqual(frame[0]["three_year_followup_end"], "2020-12-31T23:59:59Z")
            self.assertEqual(audit(path)[1], frame)

    def test_rejects_duplicate_records(self):
        row = {"arxiv_id": "a", "published": "2017-01-01T00:00:00Z", "updated": "2017-01-01T00:00:00Z", "screen_matches": []}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.jsonl.gz"
            with gzip.open(path, "wt", encoding="utf-8") as stream:
                stream.write((json.dumps(row) + "\n") * 2)
            with self.assertRaisesRegex(ValueError, "duplicate"):
                audit(path)


if __name__ == "__main__":
    unittest.main()
