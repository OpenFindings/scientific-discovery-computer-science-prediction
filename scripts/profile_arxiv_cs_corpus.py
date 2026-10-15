#!/usr/bin/env python3
"""Create a first-pass, descriptive profile of the harvested arXiv CS corpus."""
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re


CORPUS = Path("data/arxiv_cs_corpus.jsonl")
MANIFEST = Path("data/arxiv_cs_manifest.json")
OUT = Path("data/arxiv_cs_profile.json")
YEAR_BANDS = {"2010-2014": (2010, 2014), "2015-2019": (2015, 2019),
              "2020-2024": (2020, 2024), "2025-2026": (2025, 2026)}
SCREEN_TERMS = {
    "foundation_models_llms": r"\b(large language models?|LLMs?|foundation models?)\b",
    "agents_tool_use": r"\b(agents?|tool use|tool[- ]using)\b",
    "software_testing": r"\b(software testing|test generation|fuzzing|test oracle)\b",
    "program_repair": r"\b(program repair|automated repair|bug repair|repairing programs)\b",
    "compilers_languages": r"\b(compilers?|programming languages?|static analysis)\b",
    "databases": r"\b(databases?|query optimization|query processing)\b",
    "distributed_cloud": r"\b(distributed systems?|cloud computing|serverless)\b",
    "security_privacy": r"\b(security|privacy|vulnerabilit(?:y|ies)|cryptograph(?:y|ic))\b",
    "robotics_embodied": r"\b(robotics?|robot learning|embodied|sim[- ]to[- ]real)\b",
    "algorithms_theory": r"\b(algorithms?|computational complexity|formal verification)\b",
    "energy_efficiency": r"\b(energy efficiency|energy consumption|power consumption)\b",
    "causal_learning": r"\b(causal representation|causal learning|causal inference)\b",
}
PATTERNS = {name: re.compile(pattern, re.IGNORECASE) for name, pattern in SCREEN_TERMS.items()}


def main():
    years = Counter()
    bands = Counter()
    categories = Counter()
    terms = Counter()
    cs_primary = 0
    cs_crosslisted_non_cs_primary = 0
    rows = 0
    abstracts = 0
    for line in CORPUS.open(encoding="utf-8"):
        row = json.loads(line)
        rows += 1
        abstract = row.get("abstract") or ""
        abstracts += bool(abstract)
        published = row.get("published")
        year = datetime.fromisoformat(published.replace("Z", "+00:00")).year if published else None
        if year is not None:
            years[str(year)] += 1
            for label, (start, end) in YEAR_BANDS.items():
                if start <= year <= end:
                    bands[label] += 1
                    break
        primary = row.get("primary_category") or "unknown"
        categories[primary] += 1
        if primary.startswith("cs."):
            cs_primary += 1
        elif any(category.startswith("cs.") for category in row.get("categories", [])):
            cs_crosslisted_non_cs_primary += 1
        for name, pattern in PATTERNS.items():
            if pattern.search(abstract) or pattern.search(row.get("title") or ""):
                terms[name] += 1

    manifest = json.loads(MANIFEST.read_text())
    profile = {
        "profiled_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "arXiv export API; full harvest manifest in data/arxiv_cs_manifest.json",
        "interpretation": "descriptive screening counts, not topic prevalence or research value",
        "unique_records": rows,
        "api_result_slots": sum(item["api_results_available"] for item in manifest["quarter_cells"].values()),
        "complete_quarter_cells": len(manifest["quarter_cells"]),
        "year_bands": dict(sorted(bands.items())),
        "year_counts": dict(sorted(years.items())),
        "primary_cs_category_records": cs_primary,
        "crosslisted_non_cs_primary_records": cs_crosslisted_non_cs_primary,
        "top_20_primary_categories": dict(categories.most_common(20)),
        "abstract_coverage": abstracts / max(rows, 1),
        "keyword_screen_hits_overlapping": dict(sorted(terms.items())),
        "keyword_screen_patterns": SCREEN_TERMS,
        "limitations": [
            "Primary categories are not mutually exclusive conceptually; cross-listing and arXiv coverage affect counts.",
            "Keyword flags are broad lexical screens, overlap, and do not identify research questions or evidence gaps.",
            "No citation-based popularity, historical outcomes, full-text limitations, or forecasts are analyzed here.",
        ],
    }
    OUT.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"unique_records": rows, "year_bands": profile["year_bands"],
                      "primary_cs_category_records": cs_primary,
                      "crosslisted_non_cs_primary_records": cs_crosslisted_non_cs_primary,
                      "top_20_primary_categories": profile["top_20_primary_categories"],
                      "keyword_screen_hits_overlapping": terms,
                      "output": str(OUT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
