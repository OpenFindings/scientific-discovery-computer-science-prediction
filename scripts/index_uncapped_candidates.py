#!/usr/bin/env python3
"""Index every topic-matching arXiv-CS paper, with no per-year/topic cap.

This is a high-recall metadata/abstract index for follow-up review, not a
full-text review or an estimate of research merit.
"""
from collections import Counter
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from screen_research_candidates import CORPUS, GAP_CUES, STRATA, TOPICS  # noqa: E402

OUT = ROOT / "data/research_candidates_uncapped.jsonl.gz"
PROFILE = ROOT / "data/research_candidates_uncapped_profile.json"


def main() -> None:
    compiled = {
        topic: (set(spec["categories"]), [re.compile(p, re.I) for p in spec["terms"]])
        for topic, spec in TOPICS.items()
    }
    topic_counts: Counter[str] = Counter()
    year_topic_counts: Counter[tuple[int, str]] = Counter()
    stratum_topic_counts: Counter[tuple[str, str]] = Counter()
    total = matched = 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with CORPUS.open(encoding="utf-8") as source, gzip.open(OUT, "wt", encoding="utf-8", newline="\n") as dest:
        for line in source:
            if not line.strip():
                continue
            row = json.loads(line)
            total += 1
            try:
                year = int(str(row.get("published", ""))[:4])
            except ValueError:
                continue
            stratum = next((name for name, (lo, hi) in STRATA.items() if lo <= year <= hi), None)
            if stratum is None:
                continue
            categories = set(row.get("categories", []))
            text = f"{row.get('title', '')} {row.get('abstract', '')}"
            matches = []
            for topic, (allowed, patterns) in compiled.items():
                if not categories.intersection(allowed):
                    continue
                hits = sum(bool(pattern.search(text)) for pattern in patterns)
                if not hits:
                    continue
                cue_names = [name for name, pattern, _ in GAP_CUES if pattern.search(text)]
                score = min(hits, 4) * 2 + 2
                score += sum(weight for name, _, weight in GAP_CUES if name in cue_names)
                matches.append({"topic": topic, "screen_score": score, "screen_cues": cue_names})
                topic_counts[topic] += 1
                year_topic_counts[(year, topic)] += 1
                stratum_topic_counts[(stratum, topic)] += 1
            if matches:
                matched += 1
                item = dict(row)
                item["screen_matches"] = matches
                item["screen_rule"] = "arXiv category + title/abstract topic phrase; score is retrieval priority only"
                dest.write(json.dumps(item, ensure_ascii=False) + "\n")
            if total % 100_000 == 0:
                print(f"scanned {total:,}; matched {matched:,}", file=sys.stderr, flush=True)

    profile = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "data/arxiv_cs_corpus.jsonl",
        "records_scanned": total,
        "uncapped_unique_papers_matched": matched,
        "topic_match_occurrences": sum(topic_counts.values()),
        "per_year_topic_cap": None,
        "topic_definitions": {topic: {"categories": spec["categories"], "term_patterns": spec["terms"]} for topic, spec in TOPICS.items()},
        "matched_by_topic": dict(sorted(topic_counts.items())),
        "matched_by_year_topic": {f"{year}|{topic}": n for (year, topic), n in sorted(year_topic_counts.items())},
        "matched_by_stratum_topic": {f"{stratum}|{topic}": n for (stratum, topic), n in sorted(stratum_topic_counts.items())},
        "interpretation": "Uncapped high-recall lexical candidate index, not all CS research, not full text, not evidence adjudication or value ranking.",
        "limitations": [
            "arXiv-only; venue-only records not in arXiv are missing",
            "category and phrase rules omit relevant papers that use different terminology",
            "metadata and abstracts cannot establish results, unresolved status, or contradictory evidence",
            "topics overlap; one paper is stored once with all matched topics",
            "2026 includes submissions only through 2026-10-11",
        ],
        "output": str(OUT.relative_to(ROOT)),
    }
    PROFILE.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records_scanned": total, "uncapped_unique_papers_matched": matched,
                      "topic_match_occurrences": sum(topic_counts.values()),
                      "output": str(OUT.relative_to(ROOT)), "profile": str(PROFILE.relative_to(ROOT))},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
