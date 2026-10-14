#!/usr/bin/env python3
"""Targeted OpenAlex snapshot for the 1,006 frame papers (no full texts, no corpus re-download).

Every response is cached under data/cs_forecast/cache/ (git-ignored) keyed by URL, so reruns do
not hit the network. Output: data/cs_forecast/snapshot_v1.jsonl, topic_years.json,
topic_pairs.json and fetch_manifest.json. No contact e-mail is sent.

    python3 scripts/fetch_openalex_frame.py [--limit N]
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/cs_forecast"
CACHE = OUT / "cache"
API = "https://api.openalex.org/works"
STATS = {"requests": 0, "cache_hits": 0, "errors": 0}
MAX_REQUESTS = 15000


def get(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode(params, safe=":|,<>")
    key = hashlib.sha256(url.encode()).hexdigest()
    path = CACHE / key[:2] / f"{key}.json"
    if path.exists():
        STATS["cache_hits"] += 1
        return json.loads(path.read_text())
    if STATS["requests"] >= MAX_REQUESTS:
        raise RuntimeError("request budget exhausted")
    for attempt in range(5):
        try:
            STATS["requests"] += 1
            with urllib.request.urlopen(url, timeout=60) as r:
                data = json.loads(r.read())
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"url": url, "data": data}))
            time.sleep(0.11)
            return {"url": url, "data": data}
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < 4:
                time.sleep(2 ** (attempt + 1))
                continue
            STATS["errors"] += 1
            return {"url": url, "error": e.code}
        except (urllib.error.URLError, TimeoutError):
            if attempt < 4:
                time.sleep(2 ** (attempt + 1))
                continue
            raise
    raise RuntimeError("unreachable")


def short(oa_id: str | None) -> str | None:
    return oa_id.rsplit("/", 1)[-1] if oa_id else None


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def abstract(inv: dict | None) -> str:
    if not inv:
        return ""
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return " ".join(w for _, w in pos)


WORK_FIELDS = ("id,doi,display_name,publication_date,publication_year,abstract_inverted_index,"
               "authorships,referenced_works,topics,primary_topic,type")


def lookup_by_doi(arxiv_ids: list[str]) -> dict:
    found = {}
    for chunk in [arxiv_ids[i:i + 40] for i in range(0, len(arxiv_ids), 40)]:
        dois = "|".join(f"10.48550/arxiv.{a}" for a in chunk)
        r = get({"filter": f"doi:{dois}", "per_page": 50, "select": WORK_FIELDS})
        for w in r.get("data", {}).get("results", []):
            aid = (w.get("doi") or "").lower().split("arxiv.")[-1]
            found[aid] = w
    return found


def title_matches(title: str, year: int) -> list[dict]:
    q = re.sub(r"[,:|!?()\[\]\"']", " ", title)
    r = get({"filter": f"title.search:{q},publication_year:{year}-{year + 3}", "per_page": 25,
             "select": "id,display_name,publication_year,doi,type"})
    want = norm_title(title)
    return [w for w in r.get("data", {}).get("results", []) if norm_title(w["display_name"]) == want]


def group_years(filt: str) -> dict:
    r = get({"filter": filt, "group_by": "publication_year"})
    return {str(g["key"]): g["count"] for g in r.get("data", {}).get("group_by", [])}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    frame, seen = [], set()
    for line in open(ROOT / "data/historical_cs_year_topic_frame.jsonl"):
        r = json.loads(line)
        if r["arxiv_id"] not in seen:
            seen.add(r["arxiv_id"])
            frame.append(r)
    frame = frame[: args.limit] if args.limit else frame
    started = datetime.now(timezone.utc).isoformat()

    by_doi = lookup_by_doi([r["arxiv_id"] for r in frame])
    records, unmatched = [], []
    ref_ids: set[str] = set()
    for i, fr in enumerate(frame):
        y = int(fr["published"][:4])
        w = by_doi.get(fr["arxiv_id"].lower())
        versions = title_matches(fr["title"], y)
        ids = {short(v["id"]) for v in versions}
        if w:
            ids.add(short(w["id"]))
        if not ids:
            unmatched.append(fr["arxiv_id"])
            continue
        if not w:  # use the earliest exact-title version for features
            first = sorted(versions, key=lambda v: v["publication_year"])[0]
            w = get({"filter": f"openalex_id:{short(first['id'])}", "select": WORK_FIELDS})
            w = w["data"]["results"][0]
        topics = [short(t["id"]) for t in (w.get("topics") or [])]
        authors = [short(a["author"]["id"]) for a in w.get("authorships", []) if a.get("author")]
        refs = [short(x) for x in w.get("referenced_works", [])]
        ref_ids.update(refs)
        records.append({
            "paper_id": fr["arxiv_id"], "year": y, "published": fr["published"],
            "frame_topic": fr["sampling_topic"], "title": fr["title"],
            "abstract": abstract(w.get("abstract_inverted_index")),
            "openalex_ids": sorted(ids), "feature_work": short(w["id"]),
            "doi_match": fr["arxiv_id"].lower() in by_doi,
            "n_authors": len(authors), "author_ids": authors,
            "primary_topic": short((w.get("primary_topic") or {}).get("id")),
            "topics": topics, "ref_ids": refs,
            "cites_by_year": group_years("cites:" + "|".join(sorted(ids))),
        })
        if i % 50 == 0:
            print(f"{i}/{len(frame)} papers, {STATS}", file=sys.stderr)

    # references: year / topic / field / title (restricted to <= cutoff later)
    ref_meta = {}
    ref_list = sorted(ref_ids)
    for chunk in [ref_list[i:i + 50] for i in range(0, len(ref_list), 50)]:
        r = get({"filter": "openalex_id:" + "|".join(chunk), "per_page": 50,
                 "select": "id,publication_year,primary_topic,display_name"})
        for w in r.get("data", {}).get("results", []):
            pt = w.get("primary_topic") or {}
            ref_meta[short(w["id"])] = {"year": w.get("publication_year"),
                                        "topic": short(pt.get("id")),
                                        "field": short((pt.get("field") or {}).get("id")),
                                        "title": w.get("display_name") or ""}
    print(f"refs done {STATS}", file=sys.stderr)

    topic_years, pair_counts, author_cache = {}, {}, {}
    for rec in records:
        y = rec["year"]
        rec["refs"] = [ref_meta[x] for x in rec.pop("ref_ids") if x in ref_meta]
        t = rec["primary_topic"]
        if t and t not in topic_years:
            topic_years[t] = group_years(f"primary_topic.id:{t}")
        pairs = list(itertools.combinations(sorted(rec["topics"]), 2))
        rec["topic_pairs"] = pairs
        for a, b in pairs:
            key = f"{a}|{b}|{y}"
            if key not in pair_counts:
                r = get({"filter": f"topics.id:{a},topics.id:{b},publication_year:<{y}",
                         "per_page": 1, "select": "id"})
                pair_counts[key] = r.get("data", {}).get("meta", {}).get("count")
        prior = {}
        for a in rec["author_ids"][:10]:
            if a not in author_cache:
                author_cache[a] = group_years(f"author.id:{a}")
            prior[a] = sum(c for yr, c in author_cache[a].items() if int(yr) < y)
        rec["author_prior_works"] = prior
    print(f"context done {STATS}", file=sys.stderr)

    with open(OUT / "snapshot_v1.jsonl", "w") as fh:
        for rec in records:
            fh.write(json.dumps(rec) + "\n")
    (OUT / "topic_years.json").write_text(json.dumps(topic_years))
    (OUT / "topic_pairs.json").write_text(json.dumps(pair_counts))
    (OUT / "fetch_manifest.json").write_text(json.dumps({
        "source": "OpenAlex API (CC0)", "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "frame_unique_papers": len(frame), "matched": len(records),
        "unmatched": unmatched, "doi_matched": sum(r["doi_match"] for r in records),
        "references_resolved": len(ref_meta), "references_requested": len(ref_ids),
        **STATS}, indent=2) + "\n")
    print(json.dumps(STATS))


if __name__ == "__main__":
    main()
