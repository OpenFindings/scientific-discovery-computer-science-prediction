#!/usr/bin/env python3
"""Screen the arXiv-CS metadata harvest into year/topic-balanced full-text candidates.

This is a transparent lexical retrieval stage, not question extraction or an
estimate of scientific value. It writes a ranked sample for human full-text
review while retaining year-by-topic denominator counts.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data/arxiv_cs_corpus.jsonl"
OUT_JSONL = ROOT / "data/research_candidate_screen.jsonl"
OUT_PROFILE = ROOT / "data/research_candidate_screen_profile.json"
PER_YEAR_TOPIC = 8

# Topic definitions combine arXiv taxonomy with title/abstract phrases. Topics
# intentionally overlap: a paper can inform more than one research community.
TOPICS: dict[str, dict[str, object]] = {
    "foundation_models": {"categories": ["cs.CL", "cs.LG", "cs.AI"], "terms": [r"\bfoundation models?\b", r"\blarge language models?\b", r"\bLLMs?\b", r"\bpretrained language models?\b"]},
    "reasoning_and_agents": {"categories": ["cs.AI", "cs.CL"], "terms": [r"\b(reasoning|planning)\b.{0,35}\b(large language models?|LLMs?|agents?)\b", r"\b(LLM|language model) agents?\b", r"\btool[- ]using agents?\b", r"\bagentic systems?\b"]},
    "agent_reliability_security": {"categories": ["cs.AI", "cs.CR", "cs.SE"], "terms": [r"\b(agents?|agentic systems?)\b.{0,45}\b(reliability|robustness|security|safety|failure|long[- ]horizon)\b", r"\b(reliability|robustness|security|safety)\b.{0,45}\b(agents?|agentic systems?)\b"]},
    "agent_memory_coordination": {"categories": ["cs.AI", "cs.MA"], "terms": [r"\b(agent|agents|LLM|language model).{0,35}(memory|multi[- ]agent|coordination)\b", r"\b(memory|multi[- ]agent|coordination).{0,35}(agent|agents|LLM|language model)\b"]},
    "continual_multimodal_learning": {"categories": ["cs.LG", "cs.CV", "cs.CL"], "terms": [r"\bcontinual learning\b", r"\bmultimodal (learning|reasoning|models?)\b", r"\bcatastrophic forgetting\b"]},
    "model_efficiency": {"categories": ["cs.LG", "cs.DC"], "terms": [r"\b(model|inference|training) (efficiency|compression|quantization)\b", r"\benergy[- ]efficient (machine learning|inference|computing)\b", r"\binference (cost|energy|latency)\b"]},
    "software_testing": {"categories": ["cs.SE"], "terms": [r"\b(software )?testing\b", r"\bfuzz(ing| testing)?\b", r"\btest generation\b", r"\btest oracle\b"]},
    "program_repair_verification": {"categories": ["cs.SE", "cs.PL"], "terms": [r"\b(program|automated|code|bug) repair\b", r"\b(program|software|code) verification\b", r"\bformal methods?\b", r"\bprogram synthesis\b"]},
    "ai_generated_code": {"categories": ["cs.SE", "cs.PL"], "terms": [r"\b(code|program) generation\b", r"\b(LLM|large language model).{0,35}(code|program|software)\b", r"\b(code|program|software).{0,35}(large language model|LLM)\b"]},
    "software_supply_chain": {"categories": ["cs.CR", "cs.SE"], "terms": [r"\b(dependency|package|software supply chain|software ecosystem)\b.{0,40}\b(security|vulnerabilit|risk|attack)\b", r"\b(vulnerabilit|attack|security)\b.{0,40}\b(dependency|package|supply chain)\b"]},
    "distributed_cloud_systems": {"categories": ["cs.DC", "cs.NI", "cs.OS"], "terms": [r"\b(distributed systems?|cloud computing|serverless|edge computing|data center)\b", r"\b(consensus|replication|fault tolerance)\b"]},
    "databases": {"categories": ["cs.DB"], "terms": [r"\b(database|databases|query optimization|query processing|transaction processing)\b"]},
    "compilers_programming_languages": {"categories": ["cs.PL", "cs.SE"], "terms": [r"\b(compilers?|programming languages?|static analysis|runtime systems?)\b", r"\bcompiler testing\b"]},
    "energy_efficient_computing": {"categories": ["cs.DC", "cs.AR"], "terms": [r"\benergy[- ]efficient computing\b", r"\b(power|energy) consumption\b", r"\bcarbon[- ]aware computing\b"]},
    "security_privacy": {"categories": ["cs.CR"], "terms": [r"\b(privacy-preserving|privacy protection|differential privacy|cryptographic protocol)\b", r"\b(security|privacy)\b.{0,45}\b(machine learning|artificial intelligence|software|systems?)\b"]},
    "robotics_embodied_ai": {"categories": ["cs.RO", "cs.AI"], "terms": [r"\brobot(ics| learning)?\b", r"\bembodied (AI|artificial intelligence|reasoning|agents?)\b", r"\bsim[- ]to[- ]real\b"]},
    "algorithms_complexity": {"categories": ["cs.DS", "cs.CC"], "terms": [r"\balgorithms?\b", r"\bcomputational complexity\b", r"\bapproximation algorithms?\b"]},
    "optimization_causal_science": {"categories": ["cs.LG", "cs.AI", "cs.DS"], "terms": [r"\b(causal inference|causal representation|causal learning)\b", r"\b(bayesian experimental design|active learning|information gain)\b", r"\bscientific discovery\b", r"\bresearch question(s)?\b"]},
}

STRATA = {
    "2010-2014": (2010, 2014),
    "2015-2019": (2015, 2019),
    "2020-2024": (2020, 2024),
    "2025-2026_partial": (2025, 2026),
}

GAP_CUES = [
    ("explicit_gap", re.compile(r"\b(open problem|open question|remains unclear|remain unclear|not yet understood|little is known|unresolved|research gap)\b", re.I), 5),
    ("limitations_future_work", re.compile(r"\b(limitation|future work|future direction|further investigation|warrants further|left for future)\b", re.I), 4),
    ("contradiction_uncertainty", re.compile(r"\b(contradict|conflict|inconsistent|mixed results|uncertain|controvers|disagree|trade[- ]off)\b", re.I), 3),
    ("empirical_comparison", re.compile(r"\b(experiment|empirical|benchmark|evaluation|replication|ablation|measure)\b", re.I), 2),
    ("falsifiable_outcome", re.compile(r"\b(improv|outperform|reduce|increase|predict|generaliz|robust|accuracy|performance)\b", re.I), 1),
]


def main() -> None:
    if not CORPUS.is_file():
        raise SystemExit(f"Missing corpus: {CORPUS}")
    compiled = {
        topic: (set(spec["categories"]), [re.compile(p, re.I) for p in spec["terms"]])
        for topic, spec in TOPICS.items()
    }
    totals: Counter[tuple[str, str]] = Counter()
    totals_by_year_topic: Counter[tuple[int, str]] = Counter()
    heaps: dict[tuple[int, str], list[tuple[int, str, dict[str, object]]]] = defaultdict(list)
    import heapq

    records_read = 0
    with CORPUS.open(encoding="utf-8") as source:
        for line in source:
            if not line.strip():
                continue
            row = json.loads(line)
            records_read += 1
            if records_read % 100_000 == 0:
                print(f"scanned {records_read:,} records", file=sys.stderr, flush=True)
            try:
                year = int(str(row.get("published", ""))[:4])
            except ValueError:
                continue
            stratum = next((name for name, (lo, hi) in STRATA.items() if lo <= year <= hi), None)
            if stratum is None:
                continue
            text = f"{row.get('title', '')} {row.get('abstract', '')}"
            categories = set(row.get("categories", []))
            for topic, (topic_categories, patterns) in compiled.items():
                # The declared taxonomy is a first-stage filter. This avoids
                # running dozens of regular expressions against unrelated
                # abstracts across the entire 1.6 GB file.
                category_hit = bool(categories & topic_categories)
                if not category_hit:
                    continue
                term_hits = sum(bool(pattern.search(text)) for pattern in patterns)
                # Category alone is not sufficient; require at least one
                # subject-specific lexical anchor within the taxonomy stratum.
                if not term_hits:
                    continue
                bucket = (stratum, topic)
                totals[bucket] += 1
                totals_by_year_topic[(year, topic)] += 1
                cue_names = []
                score = min(term_hits, 4) * 2 + (2 if category_hit else 0)
                for name, pattern, weight in GAP_CUES:
                    if pattern.search(text):
                        cue_names.append(name)
                        score += weight
                record = {
                    "arxiv_id": row.get("arxiv_id"),
                    "versioned_id": row.get("versioned_id"),
                    "title": row.get("title"),
                    "published": row.get("published"),
                    "updated": row.get("updated"),
                    "primary_category": row.get("primary_category"),
                    "categories": row.get("categories", []),
                    "journal_reference": row.get("journal_reference"),
                    "doi": row.get("doi"),
                    "abstract": row.get("abstract"),
                    "abstract_url": row.get("abstract_url"),
                    "pdf_url": row.get("pdf_url"),
                    "screen_topic": topic,
                    "screen_stratum": stratum,
                    "screen_year": year,
                    "screen_score": score,
                    "screen_cues": cue_names,
                    "screen_rule": "topic lexical anchor + explicit gap/evidence cue score; not a scientific-value score",
                }
                key = (year, topic)
                item = (score, str(row.get("arxiv_id", "")), record)
                if len(heaps[key]) < PER_YEAR_TOPIC:
                    heapq.heappush(heaps[key], item)
                elif item[:2] > heaps[key][0][:2]:
                    heapq.heapreplace(heaps[key], item)

    selected = []
    for bucket, heap in heaps.items():
        selected.extend(item[2] for item in heap)
    selected.sort(key=lambda r: (r["screen_year"], r["screen_topic"], -int(r["screen_score"]), str(r["arxiv_id"])))
    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSONL.open("w", encoding="utf-8") as destination:
        for row in selected:
            destination.write(json.dumps(row, ensure_ascii=False) + "\n")

    profile = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "data/arxiv_cs_corpus.jsonl",
        "records_scanned": records_read,
        "strata": {name: {"years": list(years), "note": "2026 observed only through corpus collection date 2026-10-11" if name == "2025-2026_partial" else ""} for name, years in STRATA.items()},
        "topic_definitions": {topic: {"categories": sorted(categories), "term_patterns": TOPICS[topic]["terms"]} for topic, (categories, _) in compiled.items()},
        "screened_counts_by_year_topic": {f"{year}|{topic}": n for (year, topic), n in sorted(totals_by_year_topic.items())},
        "screened_counts_by_stratum_topic": {f"{s}|{t}": n for (s, t), n in sorted(totals.items())},
        "candidate_limit_per_year_topic": PER_YEAR_TOPIC,
        "selected_records": len(selected),
        "selected_counts_by_year_topic": {f"{year}|{topic}": len(heaps[(year, topic)]) for year, topic in sorted(heaps)},
        "scoring": "Lexical relevance (topic phrases plus optional arXiv category) and explicit gap/limitation/contradiction/empirical/falsifiable cues. It is a retrieval priority only, not a value ranking, evidence adjudication, or full-text result.",
        "limitations": [
            "arXiv-only coverage; venue-only literature is absent",
            "topic terms and categories are imperfect and topics overlap",
            "abstract language cannot verify whether an issue remains unresolved today",
            "no citations, current attention, or model-generated judgments enter the score",
            "ranked records require full-text/version/venue review and independent contradictory-evidence search",
        ],
        "outputs": {"candidates_jsonl": str(OUT_JSONL.relative_to(ROOT)), "profile_json": str(OUT_PROFILE.relative_to(ROOT))},
    }
    OUT_PROFILE.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records_scanned": records_read, "topic_count": len(TOPICS), "screened_year_topic_cells": len(totals_by_year_topic), "selected_records": len(selected), "per_year_topic_cap": PER_YEAR_TOPIC, "output": str(OUT_JSONL.relative_to(ROOT)), "profile": str(OUT_PROFILE.relative_to(ROOT))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
