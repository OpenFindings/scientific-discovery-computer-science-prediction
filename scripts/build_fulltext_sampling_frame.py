#!/usr/bin/env python3
"""Create a reproducible, uncapped-source stratified frame for full-text review.

The source pool is the entire uncapped lexical candidate index. Sampling is
random within declared topic × historical-period cells; it is not an evidence
screen or a quality ranking. Overlapping papers may occur in multiple cells.
"""
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/research_candidates_uncapped.jsonl.gz"
OUTPUT = ROOT / "data/fulltext_stratified_sample.jsonl"
PROFILE = ROOT / "data/fulltext_stratified_sample_profile.json"
SEED = "cs-literature-fulltext-frame-2026-10-11-v1"
PER_CELL = 3
PERIODS = {
    "2010-2014": (2010, 2014),
    "2015-2019": (2015, 2019),
    "2020-2024": (2020, 2024),
    "2025-2026-through-10-11": (2025, 2026),
}


def stable_rank(key: str) -> str:
    return hashlib.sha256(f"{SEED}|{key}".encode()).hexdigest()


def main() -> None:
    cells: dict[tuple[str, str], list[dict]] = defaultdict(list)
    records = 0
    with gzip.open(SOURCE, "rt", encoding="utf-8") as source:
        for line in source:
            row = json.loads(line)
            records += 1
            year = int(row["published"][:4])
            period = next((name for name, (lo, hi) in PERIODS.items() if lo <= year <= hi), None)
            if period is None:
                continue
            for match in row.get("screen_matches", []):
                topic = match["topic"]
                item = dict(row)
                match_evidence = next(
                    m for m in row.get("screen_matches", []) if m["topic"] == topic
                )
                item["sampling_topic"] = topic
                item["sampling_period"] = period
                item["screen_match_evidence"] = match_evidence
                item["sampling_seed"] = SEED
                item["source_pool"] = "data/research_candidates_uncapped.jsonl.gz"
                item["fulltext_urls"] = [
                    f"https://arxiv.org/html/{row['arxiv_id']}",
                    f"https://arxiv.org/pdf/{row['arxiv_id']}",
                ]
                cells[(topic, period)].append(item)

    selected = []
    cell_counts = {}
    for (topic, period), rows in sorted(cells.items()):
        hash_order = sorted(rows, key=lambda r: stable_rank(f"{topic}|{period}|{r['versioned_id']}"))
        random_rows = []
        for row in hash_order[:PER_CELL]:
            sampled = dict(row)
            sampled["sampling_arm"] = "uniform_random"
            sampled["sampling_method"] = "deterministic uniform hash-priority sample within topic-period cell"
            random_rows.append(sampled)
        priority_order = sorted(
            rows,
            key=lambda r: (
                -r["screen_match_evidence"]["screen_score"],
                stable_rank(f"priority|{topic}|{period}|{r['versioned_id']}"),
            ),
        )
        priority_rows = []
        for row in priority_order[:PER_CELL]:
            sampled = dict(row)
            sampled["sampling_arm"] = "lexical_priority"
            sampled["sampling_method"] = "top screen-score papers in topic-period cell; hash resolves ties"
            priority_rows.append(sampled)
        cell_counts[f"{topic}|{period}"] = {
            "pool": len(rows),
            "uniform_random_selected": len(random_rows),
            "lexical_priority_selected": len(priority_rows),
        }
        selected.extend(random_rows)
        selected.extend(priority_rows)

    selected.sort(key=lambda r: (r["sampling_topic"], r["sampling_period"], r["sampling_arm"], r["versioned_id"]))
    OUTPUT.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in selected),
        encoding="utf-8",
    )
    unique = len({row["arxiv_id"] for row in selected})
    profile = {
        "source": "data/research_candidates_uncapped.jsonl.gz",
        "candidate_records_scanned": records,
        "sampling_seed": SEED,
        "sampling_arms": {
            "uniform_random": "deterministic uniform hash-priority sample within each cell, useful for estimating lexical-screen precision",
            "lexical_priority": "top lexical screen-score papers within each cell, useful for discovery but intentionally score-biased",
        },
        "per_cell_target": PER_CELL,
        "periods": PERIODS,
        "selected_topic_period_rows": len(selected),
        "unique_base_arxiv_ids": unique,
        "cell_counts": cell_counts,
        "interpretation": "A reproducible full-text review frame. Random and lexical-priority arms must be analyzed separately; this is not a census, evidence adjudication, or claim that selected full texts have already been read.",
        "output": str(OUTPUT.relative_to(ROOT)),
    }
    PROFILE.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: profile[k] for k in ("candidate_records_scanned", "selected_topic_period_rows", "unique_base_arxiv_ids", "sampling_arms", "output")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
