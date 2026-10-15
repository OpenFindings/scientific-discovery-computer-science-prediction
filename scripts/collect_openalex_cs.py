#!/usr/bin/env python3
"""Build a reproducible, topic- and time-stratified open-CS paper corpus.

This is a bounded discovery corpus, not a census of all computer-science
papers. It uses OpenAlex full-text search over four publication-date strata,
keeps open-access works, and deduplicates by OpenAlex work ID.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API = "https://api.openalex.org/works"
OUT = Path("data/openalex_cs_corpus.jsonl")
MANIFEST = Path("data/openalex_collection_manifest.json")
CHECKPOINT = Path("data/openalex_collection_checkpoint.json")
PER_STRATUM = 200
PAGE_SIZE = 100
STRATA = [
    ("2010-2014", "2010-01-01", "2014-12-31"),
    ("2015-2019", "2015-01-01", "2019-12-31"),
    ("2020-2022", "2020-01-01", "2022-12-31"),
    ("2023-2026", "2023-01-01", "2026-10-11"),
]
TOPICS = {
    "artificial_intelligence": "artificial intelligence",
    "machine_learning": "machine learning",
    "natural_language_processing": "natural language processing",
    "llm_agents": "large language models agents tool use",
    "ai_safety": "AI safety robustness interpretability",
    "software_engineering": "software engineering empirical study",
    "software_testing": "software testing fuzzing debugging",
    "programming_languages": "programming languages compilers static analysis",
    "computer_systems": "computer systems operating systems architecture",
    "distributed_cloud": "distributed systems cloud computing",
    "databases": "database systems query processing",
    "computer_networks": "computer networks routing wireless",
    "cybersecurity": "computer security vulnerability privacy",
    "robotics": "robotics robot learning manipulation",
    "human_computer_interaction": "human-computer interaction interfaces",
    "algorithms_theory": "algorithms computational complexity theory",
    "computer_vision": "computer vision image understanding",
    "data_management": "data mining information retrieval knowledge graphs",
}
SELECT = ",".join((
    "id", "doi", "title", "publication_year", "publication_date", "type",
    "authorships", "primary_location", "open_access", "biblio", "ids",
    "abstract_inverted_index", "cited_by_count", "referenced_works_count", "topics",
))


def abstract_from_index(index: dict | None) -> str | None:
    if not index:
        return None
    words: dict[int, str] = {}
    for word, positions in index.items():
        for position in positions:
            words[position] = word
    return " ".join(words[position] for position in sorted(words))


def compact(work: dict, topic_key: str, query: str, period: str) -> dict:
    authors = []
    for authorship in work.get("authorships", []):
        author = authorship.get("author") or {}
        if author.get("display_name"):
            authors.append(author["display_name"])
    location = work.get("primary_location") or {}
    source = location.get("source") or {}
    oa = work.get("open_access") or {}
    best = work.get("best_oa_location") or location
    landing = best.get("landing_page_url") or best.get("pdf_url")
    topics = []
    for item in work.get("topics", [])[:5]:
        topics.append({"name": item.get("display_name"), "score": item.get("score")})
    return {
        "openalex_id": work.get("id"), "doi": work.get("doi"), "title": work.get("title"),
        "year": work.get("publication_year"), "date": work.get("publication_date"),
        "type": work.get("type"), "authors": authors,
        "venue": source.get("display_name"), "venue_type": source.get("type"),
        "is_open_access": oa.get("is_oa"), "oa_status": oa.get("oa_status"),
        "oa_url": landing, "license": best.get("license"),
        "abstract": abstract_from_index(work.get("abstract_inverted_index")),
        "cited_by_count_at_collection": work.get("cited_by_count"),
        "referenced_works_count": work.get("referenced_works_count"),
        "topics": topics, "retrieved_via": {"topic": topic_key, "query": query, "period": period},
        "retrieval_matches": [{"topic": topic_key, "query": query, "period": period}],
    }


def request_page(params: dict) -> dict:
    url = API + "?" + urlencode(params)
    request = Request(url, headers={"User-Agent": "ScientificDiscoveryOpenLiterature/1.0"})
    for attempt in range(10):
        try:
            with urlopen(request, timeout=45) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 9:
                raise
            retry_after = error.headers.get("Retry-After") if error.headers else None
            delay = float(retry_after) if retry_after and retry_after.isdigit() else min(2 ** (attempt + 1), 120)
            time.sleep(delay)
        except (URLError, TimeoutError):
            if attempt == 9:
                raise
            time.sleep(min(2 ** (attempt + 1), 120))
    raise RuntimeError("unreachable retry state")


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    records: dict[str, dict] = {}
    if OUT.exists():
        for line in OUT.read_text().splitlines():
            if line.strip():
                record = json.loads(line)
                if not record.get("title"):
                    continue
                if "retrieval_matches" not in record:
                    record["retrieval_matches"] = [record["retrieved_via"]]
                records[record["openalex_id"]] = record

    checkpoint = json.loads(CHECKPOINT.read_text()) if CHECKPOINT.exists() else {"completed": {}}
    strata_results: dict[str, dict] = checkpoint.get("completed", {})
    requests = 0
    for topic_key, query in TOPICS.items():
        topic_cells = [f"{topic_key}:{period}" for period, _, _ in STRATA]
        if all(cell in strata_results for cell in topic_cells):
            print(f"{topic_key:26s} already complete; skipping", flush=True)
            continue
        for period, start, end in STRATA:
            cell = f"{topic_key}:{period}"
            if cell in strata_results:
                continue
            cursor = "*"
            retrieved = 0
            while retrieved < PER_STRATUM:
                page_size = min(PAGE_SIZE, PER_STRATUM - retrieved)
                params = {
                    "search": query,
                    "filter": f"from_publication_date:{start},to_publication_date:{end},open_access.is_oa:true",
                    "per-page": page_size,
                    "cursor": cursor,
                    "select": SELECT,
                }
                payload = request_page(params)
                requests += 1
                batch = payload.get("results", [])
                if not batch:
                    break
                for work in batch:
                    if work.get("id") and work.get("title"):
                        record = records.get(work["id"])
                        match = {"topic": topic_key, "query": query, "period": period}
                        if record is None:
                            records[work["id"]] = compact(work, topic_key, query, period)
                        elif match not in record.setdefault("retrieval_matches", []):
                            record["retrieval_matches"].append(match)
                retrieved += len(batch)
                cursor = (payload.get("meta") or {}).get("next_cursor")
                if not cursor or len(batch) < page_size:
                    break
                time.sleep(1.0)
            strata_results[cell] = {"retrieved": retrieved, "query": query}
            CHECKPOINT.write_text(json.dumps({"completed": strata_results}, ensure_ascii=False, indent=2) + "\n")
            print(f"{topic_key:26s} {period}: {retrieved:4d} retrieved; {len(records):6d} unique", flush=True)
            # Checkpoint after every topic/time cell so interruptions are recoverable.
            OUT.write_text("".join(json.dumps(records[key], ensure_ascii=False, separators=(",", ":")) + "\n"
                                    for key in sorted(records)))

    years = Counter(str(record["year"]) for record in records.values() if record.get("year") is not None)
    topic_counts = Counter(match["topic"] for record in records.values()
                           for match in record.get("retrieval_matches", []))
    manifest = {
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider": "OpenAlex Works API",
        "provider_docs": "https://docs.openalex.org/api-entities/works",
        "collection_type": "topic- and time-stratified discovery corpus; not exhaustive census",
        "date_strata": [{"label": label, "from": start, "to": end} for label, start, end in STRATA],
        "topics": TOPICS,
        "open_access_only": True,
        "max_results_per_topic_per_stratum": PER_STRATUM,
        "requested_results_before_deduplication": sum(item["retrieved"] for item in strata_results.values()),
        "unique_openalex_works": len(records), "api_requests": requests,
        "api_requests_this_run": requests,
        "years": dict(sorted(years.items())), "first_retrieval_topic_counts": dict(sorted(topic_counts.items())),
        "strata": strata_results,
        "fields": ["title", "abstract", "authors", "publication date", "type", "venue", "OA URL/license",
                   "OpenAlex topics", "collection-time citation count", "reference count"],
        "limitations": [
            "OpenAlex coverage and full-text search are incomplete; topic search is not a systematic database census.",
            "A per-topic/per-period cap favors relevance-ranked records and truncates large result sets.",
            "Open-access availability does not imply a license permitting redistribution of full text.",
            "Citation counts are collection-time metadata and must not be used as historical pre-cutoff features.",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"unique_works": len(records), "requested_before_deduplication": manifest["requested_results_before_deduplication"],
                      "api_requests": requests, "years": dict(sorted(years.items())), "output": str(OUT),
                      "manifest": str(MANIFEST)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
