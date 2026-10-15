#!/usr/bin/env python3
"""Validate the source-cited literature question inventory without scoring it."""
from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import urlparse


path = Path("data/research_questions.jsonl")
records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
source_path = Path("data/literature_sources.jsonl")
sources = [json.loads(line) for line in source_path.read_text().splitlines() if line.strip()]
required = {"id", "domain", "question", "evidence_basis", "experiment_suggestion", "sources", "source_ids", "evidence_status"}
errors = []
for index, record in enumerate(records, 1):
    missing = required - record.keys()
    if missing:
        errors.append(f"line {index}: missing {sorted(missing)}")
    if not record.get("sources"):
        errors.append(f"line {index}: no source URL")
    for url in record.get("sources", []):
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc not in {"arxiv.org", "www.arxiv.org"}:
            errors.append(f"line {index}: unexpected source URL {url}")
ids = [record.get("id") for record in records]
if len(ids) != len(set(ids)):
    errors.append("duplicate question IDs")
source_ids = {re.sub(r"v\d+$", "", record["arxiv_id"]) for record in sources}
if len(source_ids) != len(sources):
    errors.append("duplicate arXiv source IDs in metadata manifest")
question_source_ids = {source.removeprefix("arXiv:") for record in records for source in record.get("source_ids", [])}
unindexed_sources = question_source_ids - source_ids
if unindexed_sources:
    errors.append(f"sources missing metadata: {sorted(unindexed_sources)}")
if errors:
    raise SystemExit("\n".join(errors))
print(json.dumps({"status": "candidate inventory validated; no forecasts computed",
                  "question_candidates": len(records),
                  "domains": dict(sorted(Counter(record["domain"] for record in records).items())),
                  "source_occurrences": sum(len(record["sources"]) for record in records),
                  "unique_source_ids": len(question_source_ids),
                  "bibliographic_records": len(sources),
                  "source_metadata_coverage": len(question_source_ids & source_ids) / len(question_source_ids),
                  "questions_with_fulltext_locators": sum(bool(record.get("source_locators")) for record in records),
                  "labels_present": sum("labels" in record for record in records)},
                 indent=2, ensure_ascii=False))
