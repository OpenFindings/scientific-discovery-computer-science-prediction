#!/usr/bin/env python3
"""Build a fixed, reproducible DOI+venue-reference sample from the full candidate pool."""
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/research_candidates_uncapped.jsonl.gz"
OUTPUT = ROOT / "data/publication_date_audit_sample.jsonl"
PROFILE = ROOT / "data/publication_date_audit_sample_profile.json"
SEED = "date-audit-v1"
BANDS = {
    "2010-2014": (2010, 2014),
    "2015-2019": (2015, 2019),
    "2020-2024": (2020, 2024),
    "2025-2026": (2025, 2026),
}
PER_BAND = 8


def main() -> None:
    frames: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    total = 0
    eligible = Counter()
    with gzip.open(SOURCE, "rt", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            total += 1
            try:
                year = int(row["published"][:4])
            except (KeyError, TypeError, ValueError):
                continue
            band = next((name for name, (lo, hi) in BANDS.items() if lo <= year <= hi), None)
            if band is None or not row.get("doi") or not row.get("journal_reference"):
                continue
            eligible[band] += 1
            key = hashlib.sha256(f"{SEED}|{row['arxiv_id']}".encode()).hexdigest()
            frames[band].append((key, row))

    chosen = []
    for band in BANDS:
        for key, row in sorted(frames[band], key=lambda pair: pair[0])[:PER_BAND]:
            chosen.append({
                "arxiv_id": row["arxiv_id"],
                "arxiv_year": int(row["published"][:4]),
                "period": band,
                "title": row.get("title"),
                "doi": row.get("doi"),
                "journal_reference": row.get("journal_reference"),
                "abstract_url": row.get("abstract_url"),
                "sample_seed": SEED,
                "selection_hash": key,
                "selection_frame": "uncapped candidates with nonempty DOI and journal_reference",
            })
    chosen.sort(key=lambda row: (row["period"], row["selection_hash"]))
    profile = {
        "source_records_scanned": total,
        "eligible_by_period": dict(eligible),
        "sample_size": len(chosen),
        "sample_by_period": dict(Counter(row["period"] for row in chosen)),
        "seed": SEED,
        "selection_rule": "within each arXiv submission-period band, sort eligible rows by SHA-256(seed|arxiv_id) and select the first 8",
        "eligibility_rule": "nonempty DOI and journal_reference in the 198,690-row uncapped arXiv-CS lexical candidate pool",
        "interpretation": "fixed stratified sample for source adjudication; not all arXiv-CS papers and not a full-text sample",
        "output": str(OUTPUT.relative_to(ROOT)),
    }
    OUTPUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in chosen), encoding="utf-8")
    PROFILE.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(profile, indent=2))


if __name__ == "__main__":
    main()
