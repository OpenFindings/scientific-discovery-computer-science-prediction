#!/usr/bin/env python3
"""Amendment 8 addendum 1: Semantic Scholar reference lists for training (929) and cohort (700).

Reference year/title from S2; topic/field from OpenAlex by DOI (arXiv refs via 10.48550/arxiv.<id>).
Writes data/prospective_2025/refs_s2.json. Raw responses cached (git-ignored).

    python3 scripts/prospective_2025_s2_refs.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/prospective_2025"
API = "https://api.semanticscholar.org/graph/v1"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    s2, oa = load("fetch_s2_frame"), load("fetch_openalex_frame")
    s2.CACHE, s2.MAX_REQUESTS, s2.MIN_INTERVAL = DATA / "s2_cache", 4000, 1.2
    oa.CACHE, oa.MAX_REQUESTS = DATA / "cache", 2000
    if not s2.KEY:
        sys.exit("S2_API_KEY is not set")
    hist = [json.loads(l)["paper_id"] for l in open(ROOT / "data/cs_forecast/snapshot_v1.jsonl")]
    pro = [json.loads(l)["paper_id"] for l in open(DATA / "snapshot.jsonl")]
    raw, failed = {}, []
    for i, pid in enumerate(hist + pro):
        r = s2.call(f"{API}/paper/arXiv:{pid}?fields=references.title,references.year,"
                    "references.externalIds")
        if r["status"] == 200:
            raw[pid] = (r["data"] or {}).get("references") or []
        else:
            failed.append({"paper_id": pid, "status": r["status"]})
        if i % 200 == 0:
            print(f"{i}/{len(hist) + len(pro)} {s2.STATS}", file=sys.stderr)
    dois = set()
    for refs in raw.values():
        for x in refs:
            ext = x.get("externalIds") or {}
            d = (ext.get("DOI") or (f"10.48550/arxiv.{ext['ArXiv']}" if ext.get("ArXiv") else "")).lower()
            if d:
                x["_doi"] = d
                dois.add(d)
    meta, dl = {}, sorted(dois)
    for k in range(0, len(dl), 40):
        r = oa.get({"filter": "doi:" + "|".join(dl[k:k + 40]), "per_page": 50,
                    "select": "doi,publication_year,primary_topic"})
        for w in r.get("data", {}).get("results", []):
            pt = w.get("primary_topic") or {}
            meta[(w.get("doi") or "").lower().replace("https://doi.org/", "")] = {
                "topic": oa.short(pt.get("id")), "field": oa.short((pt.get("field") or {}).get("id"))}
    out = {}
    for pid, refs in raw.items():
        out[pid] = [{"year": x.get("year"), "title": x.get("title") or "",
                     **meta.get(x.get("_doi", ""), {"topic": None, "field": None})} for x in refs]
    (DATA / "refs_s2.json").write_text(json.dumps(out))
    n_refs = sum(len(v) for v in out.values())
    matched = sum(1 for v in out.values() for x in v if x["topic"])
    (DATA / "refs_s2_manifest.json").write_text(json.dumps({
        "papers_requested": len(hist) + len(pro), "papers_ok": len(out), "failed": failed,
        "references": n_refs, "references_with_openalex_topic": matched,
        "s2": s2.STATS, "openalex": oa.STATS}, indent=1) + "\n")
    print(json.dumps({"papers_ok": len(out), "failed": len(failed), "refs": n_refs,
                      "topic_matched": matched, "s2": s2.STATS, "oa": oa.STATS}))


if __name__ == "__main__":
    main()
