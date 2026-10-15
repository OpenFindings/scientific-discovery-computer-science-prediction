#!/usr/bin/env python3
"""Select a source-only, title-screened historical observability pilot."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
from pathlib import Path
import re

SEED = "hcs-observable-title-2026-10-14-v1"
COHORT_ID = "HCS-OBSERVABLE-16-2026-10-14"
TOPICS = ("algorithms_complexity", "program_repair_verification", "security_privacy", "software_testing")
YEARS = (2017, 2018, 2019, 2020)
TITLE_PATTERN = r"algorithm|bound|complexity|hardness|verify|verification|testing|fault|bug|benchmark|performance|privacy|secure|security|correctness|optimal|repair"
EXCLUDED_PILOTS = {"2006.15074", "2012.08387", "2101.11149", "2112.15485"}


def select(frame: list[dict], old_cohort: list[dict]) -> tuple[list[dict], dict]:
    excluded = {r["arxiv_id"] for r in old_cohort} | EXCLUDED_PILOTS
    pattern = re.compile(TITLE_PATTERN, re.I)
    cells: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for row in frame:
        year = int(row["as_of"][:4])
        if row["sampling_topic"] not in TOPICS or year not in YEARS:
            continue
        if row["arxiv_id"] in excluded or not pattern.search(row["title"]):
            continue
        if row["updated"] > row["as_of"]:
            raise ValueError(f"future revision in frame: {row['arxiv_id']}")
        cells[(row["sampling_topic"], year)].append(row)
    selected, counts, seen = [], {}, set()
    for topic in TOPICS:
        for year in YEARS:
            pool = cells[(topic, year)]
            counts[f"{topic}|{year}"] = len(pool)
            if not pool:
                raise ValueError(f"empty source-only cell {topic}|{year}")
            ordered = sorted(pool, key=lambda r: (sha256(f"{SEED}|{topic}|{year}|{r['arxiv_id']}".encode()).hexdigest(), r["arxiv_id"]))
            row = next((r for r in ordered if r["arxiv_id"] not in seen), None)
            if row is None:
                raise ValueError(f"all candidate IDs overlap: {topic}|{year}")
            seen.add(row["arxiv_id"])
            followup_end = datetime(year + 5, 12, 31, 23, 59, 59, tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            selected.append({
                "cohort_id": COHORT_ID,
                "arxiv_id": row["arxiv_id"],
                "versioned_id": row["versioned_id"],
                "title": row["title"],
                "sampling_topic": topic,
                "as_of": row["as_of"],
                "five_year_followup_end": followup_end,
                "source_pdf_url": row["pdf_url"],
                "source_screen_status": "pending",
                "outcome_status": "sealed_not_searched"
            })
    return selected, {"cohort_id": COHORT_ID, "protocol": "research/historical_evidence_trajectory_protocol_v1.json",
                      "seed": SEED, "cell_pool_sizes_after_source_only_filter": counts,
                      "selected_rows": len(selected), "excluded_prior_blind_ids": len({r["arxiv_id"] for r in old_cohort}),
                      "selection_uses_future_outcomes": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame", type=Path, default=Path("data/historical_cs_year_topic_frame.jsonl"))
    parser.add_argument("--old-cohort", type=Path, default=Path("data/historical_cs_blind_cohort_20.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/historical_cs_observable_cohort_16.jsonl"))
    parser.add_argument("--profile", type=Path, default=Path("research/historical_observable_cohort_protocol.json"))
    args = parser.parse_args()
    frame = [json.loads(line) for line in args.frame.read_text().splitlines()]
    old = [json.loads(line) for line in args.old_cohort.read_text().splitlines()]
    selected, profile = select(frame, old)
    args.output.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in selected))
    args.profile.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(profile, ensure_ascii=False))


if __name__ == "__main__":
    main()
