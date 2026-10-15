#!/usr/bin/env python3
"""Validate arXiv CS collection rows and report historical/source coverage."""
from collections import Counter
from datetime import datetime
import json
from pathlib import Path


path = Path("data/arxiv_cs_corpus.jsonl")
manifest_path = Path("data/arxiv_cs_manifest.json")
checkpoint_path = Path("data/arxiv_cs_checkpoint.json")
errors = []
records = 0
seen = set()
years = Counter()
primary_categories = Counter()
abstract_count = 0
pdf_count = 0
quarter_counts = Counter()
primary_cs_count = 0
crosslisted_non_cs_primary = 0
for line_number, line in enumerate(path.open(encoding="utf-8"), 1):
    if not line.strip():
        continue
    try:
        row = json.loads(line)
    except json.JSONDecodeError as error:
        errors.append(f"line {line_number}: invalid JSON ({error})")
        continue
    arxiv_id = row.get("arxiv_id")
    if not arxiv_id or not row.get("title"):
        errors.append(f"line {line_number}: missing canonical ID or title")
        continue
    if arxiv_id in seen:
        errors.append(f"line {line_number}: duplicate arXiv ID {arxiv_id}")
        continue
    seen.add(arxiv_id)
    records += 1
    published = row.get("published")
    if published:
        year = datetime.fromisoformat(published.replace("Z", "+00:00")).year
        years[str(year)] += 1
    primary = row.get("primary_category")
    if primary:
        primary_categories[primary] += 1
        primary_cs_count += primary.startswith("cs.")
        crosslisted_non_cs_primary += (not primary.startswith("cs.")
                                       and any(category.startswith("cs.") for category in row.get("categories", [])))
    abstract_count += bool(row.get("abstract"))
    pdf_count += bool(row.get("pdf_url"))
    quarter = row.get("retrieved_via", {}).get("submitted_date_stratum")
    if quarter:
        quarter_counts[quarter] += 1

if errors:
    raise SystemExit("\n".join(errors[:30]))

manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
checkpoint = json.loads(checkpoint_path.read_text()).get("completed", {}) if checkpoint_path.exists() else {}
quarter_api_results = sum(item.get("api_results_available", 0) for item in checkpoint.values())
quarter_api_retrieved = sum(item.get("api_results_returned", 0) for item in checkpoint.values())
incomplete_quarters = {quarter: {"retrieved": item.get("api_results_returned", 0),
                                 "available": item.get("api_results_available", 0)}
                       for quarter, item in checkpoint.items()
                       if item.get("api_results_returned", 0) < item.get("api_results_available", 0)}

print(json.dumps({
    "status": "valid deduplicated arXiv CS discovery corpus; not all CS venues",
    "unique_papers": records,
    "quarter_cells": len(checkpoint),
    "quarter_api_results_available": quarter_api_results,
    "quarter_api_results_retrieved": quarter_api_retrieved,
    "incomplete_quarters": incomplete_quarters,
    "year_min": min(map(int, years)) if years else None,
    "year_max": max(map(int, years)) if years else None,
    "year_counts": dict(sorted(years.items())),
    "abstract_coverage": abstract_count / max(records, 1),
    "pdf_link_coverage": pdf_count / max(records, 1),
    "primary_cs_category_records": primary_cs_count,
    "crosslisted_with_non_cs_primary_category": crosslisted_non_cs_primary,
    "primary_category_counts": dict(sorted(primary_categories.items())),
    "retrieval_quarter_counts": dict(sorted(quarter_counts.items())),
    "unique_ids": len(seen) == records,
}, ensure_ascii=False, indent=2))
