#!/usr/bin/env python3
"""Fetch Semantic Scholar records and citing-paper years for the 1,006 frame papers.

Amendment 1 (research/preregistration_cs_breakthrough_forecast_v1_amendment1_s2.md). Raw
responses are cached under data/cs_forecast_s2/cache/ (git-ignored; S2 licence) and never
summarized here: outcomes are computed only by scripts/analyze_cs_label_cross_source.py.
The key is read from S2_API_KEY, sent as x-api-key, and never written to disk.

    python3 scripts/fetch_s2_frame.py [--limit N]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/cs_forecast_s2"
CACHE = OUT / "cache"
API = "https://api.semanticscholar.org/graph/v1"
MAX_REQUESTS = 6000
MIN_INTERVAL = 1.05  # seconds; S2 introductory limit is 1 request/second
STATS = {"requests": 0, "cache_hits": 0, "errors": 0}
KEY = os.environ.get("S2_API_KEY", "").strip()
_last = [0.0]


def call(url: str, body: dict | None = None) -> dict:
    key = hashlib.sha256((url + json.dumps(body, sort_keys=True)).encode()).hexdigest()
    path = CACHE / key[:2] / f"{key}.json"
    if path.exists():
        STATS["cache_hits"] += 1
        return json.loads(path.read_text())
    if STATS["requests"] >= MAX_REQUESTS:
        raise RuntimeError("request budget exhausted (amendment 1 cap: 6,000)")
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(6):
        wait = _last[0] + MIN_INTERVAL - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(url, data=data, method="POST" if data else "GET")
        req.add_header("x-api-key", KEY)
        if data:
            req.add_header("Content-Type", "application/json")
        STATS["requests"] += 1
        _last[0] = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                rec = {"url": url, "body": body, "status": r.status,
                       "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                       "data": json.loads(r.read())}
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 5:
                time.sleep(2 ** (attempt + 1))
                continue
            STATS["errors"] += 1
            rec = {"url": url, "body": body, "status": e.code,
                   "retrieved_utc": datetime.now(timezone.utc).isoformat(), "data": None}
            break
        except (urllib.error.URLError, TimeoutError):
            if attempt < 5:
                time.sleep(2 ** (attempt + 1))
                continue
            raise
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec))
    return rec


def citing_years(paper_id: str) -> tuple[list, bool]:
    """All citing-paper years for one S2 paper, following offset/next to the end."""
    years, offset = [], 0
    while True:
        r = call(f"{API}/paper/{paper_id}/citations?fields=year,externalIds&limit=1000"
                 f"&offset={offset}")
        if r["status"] != 200:
            return years, False
        page = r["data"].get("data", [])
        years.extend((c.get("citingPaper") or {}).get("year") for c in page)
        if "next" not in r["data"] or not page:
            return years, True
        offset = r["data"]["next"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    if not KEY:
        sys.exit("S2_API_KEY is not set")
    OUT.mkdir(parents=True, exist_ok=True)
    ids, seen = [], set()
    for line in open(ROOT / "data/historical_cs_year_topic_frame.jsonl"):
        a = json.loads(line)["arxiv_id"]
        if a not in seen:
            seen.add(a)
            ids.append(a)
    ids = ids[: args.limit] if args.limit else ids
    started = datetime.now(timezone.utc).isoformat()

    found = {}
    for i in range(0, len(ids), 500):
        chunk = ids[i:i + 500]
        r = call(f"{API}/paper/batch?fields=paperId,externalIds,title,year",
                 {"ids": [f"arXiv:{a}" for a in chunk]})
        for a, p in zip(chunk, r["data"] or []):
            if p:
                found[a] = p["paperId"]
    complete, incomplete = 0, []
    for j, (a, pid) in enumerate(found.items()):
        _, ok = citing_years(pid)
        complete += ok
        if not ok:
            incomplete.append(a)
        if j % 100 == 0:
            print(f"{j}/{len(found)} papers, {STATS}", file=sys.stderr)

    (OUT / "fetch_manifest.json").write_text(json.dumps({
        "source": "Semantic Scholar Academic Graph API", "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "frame_unique_papers": len(ids), "s2_matched": len(found),
        "unmatched": sorted(set(ids) - set(found)), "citations_complete": complete,
        "citations_incomplete": incomplete, **STATS}, indent=2) + "\n")
    print(json.dumps({"s2_matched": len(found), "citations_complete": complete, **STATS}))


if __name__ == "__main__":
    main()
