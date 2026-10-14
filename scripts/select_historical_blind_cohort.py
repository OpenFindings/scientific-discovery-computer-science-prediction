#!/usr/bin/env python3
"""Freeze a small, cross-domain question-screening cohort before follow-up search."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path


TOPICS = ("ai_generated_code", "algorithms_complexity", "databases", "security_privacy", "software_testing")
YEARS = (2018, 2019, 2020, 2021)
EXCLUDED_PILOTS = frozenset(("2112.15485", "2006.15074", "2012.08387", "2101.11149"))
SEED = "cs-historical-blind-cohort-2026-10-14-v1"


def select(frame: list[dict]) -> tuple[list[dict], dict]:
    cells: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for row in frame:
        topic = row["sampling_topic"]
        year = int(row["as_of"][:4])
        if topic in TOPICS and year in YEARS and row["arxiv_id"] not in EXCLUDED_PILOTS:
            if row["updated"] > row["as_of"]:
                raise ValueError(f"future revision in frame: {row['arxiv_id']}")
            cells[(topic, year)].append(row)
    cohort = []
    pools = {}
    already_selected = set()
    for topic in TOPICS:
        for year in YEARS:
            pool = cells[(topic, year)]
            if not pool:
                raise ValueError(f"empty cell {topic}/{year}")
            pools[f"{topic}|{year}"] = len(pool)
            candidates = sorted(pool, key=lambda row: hashlib.sha256(
                f"{SEED}|{topic}|{year}|{row['arxiv_id']}".encode()).hexdigest())
            chosen = next((row for row in candidates if row["arxiv_id"] not in already_selected), None)
            if chosen is None:
                raise ValueError(f"all candidates overlap earlier cells: {topic}/{year}")
            already_selected.add(chosen["arxiv_id"])
            cohort.append({
                "cohort_id": "HCS-BLIND-20-2026-10-14",
                "arxiv_id": chosen["arxiv_id"],
                "versioned_id": chosen["versioned_id"],
                "title": chosen["title"],
                "sampling_topic": topic,
                "as_of": chosen["as_of"],
                "three_year_followup_end": chosen["three_year_followup_end"],
                "source_pdf_url": chosen["pdf_url"],
                "source_abstract_url": chosen["abstract_url"],
                "source_fulltext_review_status": "pending",
                "question_status": "pending",
                "future_outcome_status": "sealed_not_searched",
            })
    profile = {
        "cohort_id": "HCS-BLIND-20-2026-10-14",
        "seed": SEED,
        "source": "data/historical_cs_year_topic_frame.jsonl",
        "topics": TOPICS,
        "years": YEARS,
        "excluded_pilot_ids": sorted(EXCLUDED_PILOTS),
        "sampling": "one hash-priority-selected, non-overlapping paper from each topic x year cell; frozen before inspecting these papers' post-cutoff outcomes",
        "cell_pool_sizes": pools,
        "selected_rows": len(cohort),
        "unique_arxiv_ids": len(already_selected),
        "purpose": "Measure question-screening yield and build a defensible historical-label pilot; not a full CS census or a held-out Paper 3 test until source screening and a label rubric are frozen.",
    }
    return cohort, profile


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame", type=Path, default=Path("data/historical_cs_year_topic_frame.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/historical_cs_blind_cohort_20.jsonl"))
    parser.add_argument("--profile", type=Path, default=Path("research/historical_cs_blind_cohort_protocol.json"))
    args = parser.parse_args()
    frame = [json.loads(line) for line in args.frame.read_text().splitlines()]
    cohort, profile = select(frame)
    args.output.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in cohort))
    args.profile.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"cohort_id": profile["cohort_id"], "selected_rows": len(cohort),
                      "unique_arxiv_ids": profile["unique_arxiv_ids"]}))


if __name__ == "__main__":
    main()
