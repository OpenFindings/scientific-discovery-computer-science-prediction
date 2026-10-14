#!/usr/bin/env python3
"""Build a broad, year-end point-in-time *metadata* frame for CS research.

This audits the latest arXiv record's `updated` field.  A record revised after
the simulated cutoff is excluded because its current abstract may leak future
information.  Selection does not adjudicate research questions or outcomes.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path


FIRST_YEAR = 2010
LAST_YEAR = 2022  # at least three subsequent complete years before 2026
PER_CELL = 5
SEED = "cs-history-year-topic-2026-10-14-v1"


def rank(topic: str, year: int, arxiv_id: str) -> str:
    return hashlib.sha256(f"{SEED}|{topic}|{year}|{arxiv_id}".encode()).hexdigest()


def audit(source: Path, per_cell: int = PER_CELL) -> tuple[dict, list[dict]]:
    if per_cell < 1:
        raise ValueError("per_cell must be positive")
    counts: Counter = Counter()
    cells: dict[tuple[int, str], list[dict]] = defaultdict(list)
    seen_ids: set[str] = set()
    with gzip.open(source, "rt", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            counts["records_scanned"] += 1
            paper_id = row["arxiv_id"]
            if paper_id in seen_ids:
                raise ValueError(f"duplicate arxiv_id: {paper_id}")
            seen_ids.add(paper_id)
            year = int(row["published"][:4])
            if not FIRST_YEAR <= year <= LAST_YEAR:
                continue
            counts["historical_lexical_candidates"] += 1
            as_of = f"{year}-12-31T23:59:59Z"
            updated = row["updated"]
            if updated < row["published"]:
                raise ValueError(f"updated before published: {paper_id}")
            eligible = updated <= as_of
            counts["year_end_eligible" if eligible else "year_end_later_revision"] += 1
            for match in row["screen_matches"]:
                topic = match["topic"]
                counts[f"topic_year_pool|{year}|{topic}"] += 1
                if eligible:
                    counts[f"topic_year_eligible|{year}|{topic}"] += 1
                    cells[(year, topic)].append(row)
    frame = []
    cell_profile = {}
    for (year, topic), rows in sorted(cells.items()):
        chosen = sorted(rows, key=lambda row: rank(topic, year, row["arxiv_id"]))[:per_cell]
        cell_profile[f"{year}|{topic}"] = {
            "eligible_pool": len(rows),
            "all_latest_record_pool": counts[f"topic_year_pool|{year}|{topic}"],
            "selected": len(chosen),
        }
        for row in chosen:
            frame.append({
                "arxiv_id": row["arxiv_id"],
                "versioned_id": row["versioned_id"],
                "title": row["title"],
                "published": row["published"],
                "updated": row["updated"],
                "abstract_url": row["abstract_url"],
                "pdf_url": row["pdf_url"],
                "sampling_topic": topic,
                "as_of": f"{year}-12-31T23:59:59Z",
                "three_year_followup_end": f"{year + 3}-12-31T23:59:59Z",
                "sampling_seed": SEED,
                "historical_status": "latest_arxiv_metadata_record_not_revised_after_year_end; outcome_not_adjudicated",
            })
    frame.sort(key=lambda row: (row["sampling_topic"], row["as_of"], row["arxiv_id"]))
    total = counts["historical_lexical_candidates"]
    report = {
        "source": str(source),
        "scope": {"first_publication_year": FIRST_YEAR, "last_publication_year": LAST_YEAR,
                  "followup_years_possible": 3, "year_end_cutoff": True},
        "records_scanned": counts["records_scanned"],
        "historical_lexical_candidates": total,
        "year_end_eligible_latest_metadata": counts["year_end_eligible"],
        "later_revised_latest_metadata_excluded": counts["year_end_later_revision"],
        "later_revision_fraction": counts["year_end_later_revision"] / total if total else None,
        "topic_year_cells_with_any_candidate": sum(key.startswith("topic_year_pool|") for key in counts),
        "topic_year_cells_excluded_entirely_due_to_later_revision": [
            key.removeprefix("topic_year_pool|") for key in sorted(counts)
            if key.startswith("topic_year_pool|") and
            "topic_year_eligible|" + key.removeprefix("topic_year_pool|") not in counts
        ],
        "sampling": {"method": "SHA-256 hash-priority within publication-year x lexical-topic cells after year-end revision filter",
                     "seed": SEED, "per_cell_target": per_cell,
                     "selected_topic_year_rows": len(frame),
                     "unique_arxiv_ids_selected": len({row["arxiv_id"] for row in frame}),
                     "cells_with_eligible_candidates": len(cell_profile)},
        "cell_profile": cell_profile,
        "interpretation": "Metadata-only frame, not a full-text review or historical forecast. Current latest-version abstracts revised after the simulated cutoff are excluded, not reconstructed. A year-end eligible latest record is a necessary but not sufficient point-in-time validity condition; titles, citations, later publications, and actual question outcomes require independent as-of verification.",
    }
    return report, frame


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("data/research_candidates_uncapped.jsonl.gz"))
    parser.add_argument("--report", type=Path, default=Path("reports/broad_cs_historical_audit.json"))
    parser.add_argument("--frame", type=Path, default=Path("data/historical_cs_year_topic_frame.jsonl"))
    args = parser.parse_args()
    report, frame = audit(args.source)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.frame.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    args.frame.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in frame))
    print(json.dumps({k: report[k] for k in ("records_scanned", "historical_lexical_candidates",
                                          "year_end_eligible_latest_metadata",
                                          "later_revised_latest_metadata_excluded", "sampling")}, indent=2))


if __name__ == "__main__":
    main()
