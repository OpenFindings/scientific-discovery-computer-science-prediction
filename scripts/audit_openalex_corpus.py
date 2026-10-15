#!/usr/bin/env python3
"""Validate the OpenAlex discovery corpus and print coverage diagnostics."""
from collections import Counter
import json
from pathlib import Path


path = Path("data/openalex_cs_corpus.jsonl")
errors = []
records = []
seen = set()
for line_number, line in enumerate(path.read_text().splitlines(), 1):
    if not line.strip():
        continue
    try:
        record = json.loads(line)
    except json.JSONDecodeError as error:
        errors.append(f"line {line_number}: invalid JSON ({error})")
        continue
    work_id = record.get("openalex_id")
    if not work_id or not work_id.startswith("https://openalex.org/W"):
        errors.append(f"line {line_number}: invalid/missing OpenAlex work ID")
    elif work_id in seen:
        errors.append(f"line {line_number}: duplicate work ID {work_id}")
    seen.add(work_id)
    if not record.get("title"):
        continue  # Preserve raw provider data; title-less rows are excluded from analysis.
    if record.get("is_open_access") is not True:
        errors.append(f"line {line_number}: record is not marked open access")
    if not (record.get("retrieval_matches") or record.get("retrieved_via")):
        errors.append(f"line {line_number}: missing retrieval provenance")
    records.append(record)

if errors:
    raise SystemExit("\n".join(errors[:30]))

years = Counter(str(record["year"]) for record in records if record.get("year") is not None)
topics = Counter(match["topic"] for record in records
                 for match in (record.get("retrieval_matches") or [record.get("retrieved_via", {})]))
print(json.dumps({
    "status": "valid discovery corpus; not a forecast or exhaustive census",
    "unique_works": len(records),
    "titleless_rows_excluded_from_analysis": sum(1 for line in path.read_text().splitlines()
        if line.strip() and not json.loads(line).get("title")),
    "year_min": min((record["year"] for record in records if record.get("year") is not None), default=None),
    "year_max": max((record["year"] for record in records if record.get("year") is not None), default=None),
    "year_counts": dict(sorted(years.items())),
    "abstract_coverage": sum(bool(record.get("abstract")) for record in records) / max(1, len(records)),
    "oa_url_coverage": sum(bool(record.get("oa_url")) for record in records) / max(1, len(records)),
    "retrieval_matches_by_topic": dict(sorted(topics.items())),
    "valid_source_ids_are_unique": len({record["openalex_id"] for record in records}) == len(records),
}, ensure_ascii=False, indent=2))
