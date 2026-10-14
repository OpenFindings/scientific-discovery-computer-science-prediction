import gzip
import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_historical_cs_frame import audit
from scripts.select_historical_blind_cohort import EXCLUDED_PILOTS, select


class HistoricalFrameTests(unittest.TestCase):
    def test_blind_cohort_source_screen_complete_without_future_leakage(self):
        root = Path(__file__).resolve().parents[1]
        cohort = {
            row["versioned_id"]: row
            for row in map(json.loads, (root / "data/historical_cs_blind_cohort_20.jsonl").read_text().splitlines())
        }
        first = json.loads((root / "reports/historical_source_screen_round1.json").read_text())
        second = json.loads((root / "reports/historical_source_screen_round2.json").read_text())
        self.assertFalse(first["future_outcomes_searched"])
        self.assertFalse(second["future_outcomes_searched"])
        self.assertEqual(second["summary"]["rows_screened"], len(second["rows"]))
        self.assertEqual(second["summary"]["eligible_source_questions"],
                         sum(r["question_status"] == "eligible_source_open" for r in second["rows"]))
        self.assertEqual(second["summary"]["ineligible_no_explicit_unresolved_question"],
                         sum(r["question_status"] == "ineligible_no_explicit_unresolved_question" for r in second["rows"]))
        self.assertEqual(second["summary"]["direct_future_outcome_labels"], 0)
        first_rows = {r["versioned_id"]: r for r in first["rows"]}
        second_rows = {r["versioned_id"]: r for r in second["rows"]}
        self.assertEqual(set(first_rows) & set(second_rows), {"1811.10861v1"})
        self.assertEqual(first_rows["1811.10861v1"]["source_status"], "fulltext_unavailable_on_attempt")
        self.assertEqual(second_rows["1811.10861v1"]["source_status"], "section_screened")
        merged = first_rows | second_rows
        self.assertEqual(set(merged), set(cohort))
        self.assertEqual(sum(r["question_status"] == "eligible_source_open" for r in merged.values()), 13)
        for versioned_id, row in merged.items():
            frozen = cohort[versioned_id]
            self.assertEqual(row["source_pdf_url"], frozen["source_pdf_url"])
            self.assertEqual(row["as_of"], frozen["as_of"])
            self.assertEqual(row["future_outcome_status"], "sealed_not_searched")
            self.assertEqual(row["source_status"], "section_screened")
            if versioned_id in second_rows:
                self.assertRegex(row["source_pdf_sha256"], r"^[0-9a-f]{64}$")
                self.assertTrue(row["source_locator"])
                self.assertTrue(row["source_basis"])
            if row["question_status"] == "eligible_source_open":
                self.assertTrue(row["candidate_question"])
                self.assertTrue(row["candidate_falsification"])
            else:
                self.assertIsNone(row["candidate_question"])

    def test_followup_triage_keeps_near_misses_unadjudicated(self):
        root = Path(__file__).resolve().parents[1]
        triage = json.loads((root / "reports/historical_blind_followup_triage_round1.json").read_text())
        screens = [json.loads((root / f"reports/historical_source_screen_round{n}.json").read_text())
                   for n in (1, 2)]
        eligible = {row["versioned_id"] for screen in screens for row in screen["rows"]
                    if row["question_status"] == "eligible_source_open"}
        ids = [row["versioned_id"] for row in triage["rows"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids) <= eligible, True)
        self.assertEqual(len(ids), triage["summary"]["questions_with_followup_search_attempted"])
        self.assertEqual(len(eligible), triage["summary"]["eligible_questions_total"])
        self.assertEqual(len(eligible) - len(ids), triage["summary"]["questions_not_yet_searched"])
        self.assertEqual(triage["summary"]["direct_resolution_labels_authenticated"], 0)
        self.assertEqual(triage["summary"]["explicitly_unresolved_labels_authenticated"], 0)
        self.assertTrue(all(row["resolution_label"] == "unadjudicated" for row in triage["rows"]))
        self.assertTrue(all(row["search_terms"] and row["match_audit"] for row in triage["rows"]))

    def test_blind_source_screen_is_cohort_bound_and_future_sealed(self):
        root = Path(__file__).resolve().parents[1]
        cohort = {
            row["versioned_id"]: row
            for row in (
                json.loads(line)
                for line in (root / "data/historical_cs_blind_cohort_20.jsonl").read_text().splitlines()
            )
        }
        screen = json.loads((root / "reports/historical_source_screen_round1.json").read_text())
        protocol = json.loads((root / "research/historical_outcome_label_protocol_v1.json").read_text())
        rows = screen["rows"]
        counts = screen["summary"]
        self.assertTrue(protocol["frozen_before_cohort_followup_search"])
        self.assertFalse(screen["future_outcomes_searched"])
        self.assertEqual(len(cohort), counts["cohort_total"])
        self.assertEqual(len(rows), counts["rows_screened_or_attempted"])
        self.assertEqual(len({row["versioned_id"] for row in rows}), len(rows))
        self.assertEqual(counts["remaining_untouched"], len(cohort) - len(rows))
        self.assertEqual(counts["original_fulltexts_section_screened"],
                         sum(row["source_status"] == "section_screened" for row in rows))
        self.assertEqual(counts["eligible_source_questions"],
                         sum(row["question_status"] == "eligible_source_open" for row in rows))
        self.assertEqual(counts["ineligible_completed_or_no_open_question"],
                         sum(row["question_status"] == "ineligible_no_explicit_unresolved_question" for row in rows))
        self.assertEqual(counts["original_fulltext_unavailable_on_this_attempt"],
                         sum(row["source_status"] == "fulltext_unavailable_on_attempt" for row in rows))
        self.assertEqual(counts["direct_future_outcome_labels"], 0)
        for row in rows:
            frozen = cohort[row["versioned_id"]]
            self.assertEqual(row["source_pdf_url"], frozen["source_pdf_url"])
            self.assertEqual(row["as_of"], frozen["as_of"])
            self.assertEqual(row["future_outcome_status"], "sealed_not_searched")
            if row["question_status"] == "eligible_source_open":
                self.assertEqual(row["source_status"], "section_screened")
                self.assertTrue(row["candidate_question"])
                self.assertTrue(row["candidate_falsification"])
                self.assertTrue(row["source_locator"])

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
