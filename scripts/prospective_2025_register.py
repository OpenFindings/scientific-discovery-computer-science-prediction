#!/usr/bin/env python3
"""Amendment 8: sample 2025 CS arXiv papers, fetch cutoff-time features, register forecasts.

Frozen in research/preregistration_cs_breakthrough_forecast_v1_amendment8_prospective_2025.md.
Never downloads citations dated after 2025. Outputs results/prospective_2025/.

    python3 scripts/prospective_2025_register.py sample     # OpenAlex sample + arXiv eligibility
    python3 scripts/prospective_2025_register.py fetch      # cutoff-time features (resumable)
    python3 scripts/prospective_2025_register.py predict    # train on history, write predictions
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cs_forecast import evaluate as ev  # noqa: E402
from cs_forecast.features import paper_features, retrieval_features  # noqa: E402
from cs_forecast.topics import primary_subfield  # noqa: E402

DATA = ROOT / "data/prospective_2025"
OUT = ROOT / "results/prospective_2025"
FILT = "publication_year:2025,primary_location.source.id:S4306400194,primary_topic.field.id:fields/17"
SEED, N_CAND, N_KEEP = 20261017, 1000, 700
CUTOFF = "2025-12-31T23:59:59Z"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


oa = load("fetch_openalex_frame")
oa.CACHE = DATA / "cache"
oa.MAX_REQUESTS = 9000


def sample() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    cands = []
    for page in range(1, N_CAND // 100 + 1):
        r = oa.get({"filter": FILT, "sample": N_CAND, "seed": SEED, "per_page": 100,
                    "page": page, "select": oa.WORK_FIELDS})
        cands += r["data"]["results"]
    ids = []
    for w in cands:
        m = re.search(r"10\.48550/arxiv\.(.+)$", (w.get("doi") or "").lower())
        ids.append(m.group(1) if m else None)
    arx = {}
    valid = [i for i in ids if i]
    for k in range(0, len(valid), 100):
        q = "https://export.arxiv.org/api/query?max_results=100&id_list=" + ",".join(valid[k:k + 100])
        with urllib.request.urlopen(q, timeout=120) as resp:
            root = ET.fromstring(resp.read())
        ns = {"a": "http://www.w3.org/2005/Atom"}
        for e in root.findall("a:entry", ns):
            aid = re.sub(r"v\d+$", "", e.find("a:id", ns).text.rsplit("/abs/", 1)[-1])
            arx[aid.lower()] = {"published": e.find("a:published", ns).text,
                                "updated": e.find("a:updated", ns).text}
        time.sleep(3.5)
    kept, reasons = [], {"no_arxiv_doi": 0, "not_in_arxiv_api": 0, "first_version_not_2025": 0,
                         "revised_after_cutoff": 0}
    for w, aid in zip(cands, ids):
        if not aid:
            reasons["no_arxiv_doi"] += 1
            continue
        a = arx.get(aid)
        if not a:
            reasons["not_in_arxiv_api"] += 1
            continue
        if not a["published"].startswith("2025"):
            reasons["first_version_not_2025"] += 1
            continue
        if a["updated"] > CUTOFF:
            reasons["revised_after_cutoff"] += 1
            continue
        if len(kept) < N_KEEP:
            kept.append({"arxiv_id": aid, "work": w, **a})
    (DATA / "cohort.json").write_text(json.dumps({
        "retrieved_utc": datetime.now(timezone.utc).isoformat(), "filter": FILT, "seed": SEED,
        "candidates": len(cands), "eligible_total": len(kept) + 0, "ineligible": reasons,
        "kept": kept}, indent=1) + "\n")
    print(json.dumps({"candidates": len(cands), "kept": len(kept), "ineligible": reasons,
                      **oa.STATS}))


def fetch() -> None:
    cohort = json.loads((DATA / "cohort.json").read_text())["kept"]
    records, ref_ids = [], set()
    for c in cohort:
        w, wid = c["work"], oa.short(c["work"]["id"])
        r = oa.get({"filter": f"cites:{wid},publication_year:2025", "per_page": 1, "select": "id"})
        c25 = r.get("data", {}).get("meta", {}).get("count")
        refs = [oa.short(x) for x in w.get("referenced_works", [])]
        ref_ids.update(refs)
        pt = w.get("primary_topic") or {}
        records.append({
            "paper_id": c["arxiv_id"], "year": 2025, "published": c["published"],
            "frame_topic": oa.short((pt.get("subfield") or {}).get("id")) or "none",
            "title": w.get("display_name") or "", "abstract": oa.abstract(w.get("abstract_inverted_index")),
            "feature_work": wid, "primary_topic": oa.short(pt.get("id")),
            "topics": [oa.short(t["id"]) for t in (w.get("topics") or [])],
            "author_ids": [oa.short(a["author"]["id"]) for a in w.get("authorships", [])
                           if a.get("author")],
            "n_authors": len(w.get("authorships", [])), "ref_ids": refs,
            "cites_by_year": {"2025": c25} if c25 is not None else {}})
    ref_meta, ref_list = {}, sorted(ref_ids)
    for k in range(0, len(ref_list), 50):
        r = oa.get({"filter": "openalex_id:" + "|".join(ref_list[k:k + 50]), "per_page": 50,
                    "select": "id,publication_year,primary_topic,display_name"})
        for x in r.get("data", {}).get("results", []):
            pt = x.get("primary_topic") or {}
            ref_meta[oa.short(x["id"])] = {"year": x.get("publication_year"),
                                           "topic": oa.short(pt.get("id")),
                                           "field": oa.short((pt.get("field") or {}).get("id")),
                                           "title": x.get("display_name") or ""}
    print("refs done", oa.STATS, file=sys.stderr)
    topic_years, pairs, authors = {}, {}, {}
    for rec in records:
        rec["refs"] = [ref_meta[x] for x in rec.pop("ref_ids") if x in ref_meta]
        t = rec["primary_topic"]
        if t and t not in topic_years:
            topic_years[t] = oa.group_years(f"primary_topic.id:{t}")
        rec["topic_pairs"] = list(itertools.combinations(sorted(rec["topics"]), 2))
        for a, b in rec["topic_pairs"]:
            key = f"{a}|{b}|2025"
            if key not in pairs:
                r = oa.get({"filter": f"topics.id:{a},topics.id:{b},publication_year:<2025",
                            "per_page": 1, "select": "id"})
                pairs[key] = r.get("data", {}).get("meta", {}).get("count")
        prior = {}
        for a in [x for x in rec["author_ids"] if x][:10]:
            if a not in authors:
                authors[a] = oa.group_years(f"author.id:{a}")
            prior[a] = sum(c for yr, c in authors[a].items() if int(yr) < 2025)
        rec["author_prior_works"] = prior
    with open(DATA / "snapshot.jsonl", "w") as fh:
        for rec in records:
            fh.write(json.dumps(rec) + "\n")
    (DATA / "topic_years.json").write_text(json.dumps(topic_years))
    (DATA / "topic_pairs.json").write_text(json.dumps(pairs))
    (DATA / "fetch_manifest.json").write_text(json.dumps(
        {"finished_utc": datetime.now(timezone.utc).isoformat(), "papers": len(records),
         **oa.STATS}, indent=1) + "\n")
    print(json.dumps({"papers": len(records), **oa.STATS}))


def frame(recs, topic_years, pairs) -> pd.DataFrame:
    rows = []
    for p in recs:
        f = paper_features(p, topic_years, pairs)
        f.update(paper_id=p["paper_id"], year=p["year"], frame_topic=p["frame_topic"],
                 title=p["title"], text=f"{p['title']}. {p.get('abstract') or ''}",
                 cs_subfield=primary_subfield(p["title"], p.get("abstract") or ""))
        rows.append(f)
    return pd.DataFrame(rows)


def posting(df: pd.DataFrame, topic_years: dict, recs: dict) -> pd.DataFrame:
    d = df.copy()
    vol, gro = [], []
    for pid, y in zip(d.paper_id, d.year):
        c = topic_years.get(recs[pid].get("primary_topic") or "", {})
        v1, v3 = c.get(str(y - 1), 0), c.get(str(y - 3), 0)
        vol.append(math.log1p(v1))
        gro.append(math.log((v1 + 1) / (v3 + 1)))
    d["env_topic_volume_log"], d["env_topic_growth"] = vol, gro
    return d.drop(columns=["base_cites_year0_log", "base_months_to_cutoff"])


def predict() -> None:
    fc = load("run_cs_forecast")
    hist = fc.build_frame()
    hrecs = {json.loads(l)["paper_id"]: json.loads(l)
             for l in open(ROOT / "data/cs_forecast/snapshot_v1.jsonl")}
    prec_list = [json.loads(l) for l in open(DATA / "snapshot.jsonl")]
    precs = {p["paper_id"]: p for p in prec_list}
    pty = json.loads((DATA / "topic_years.json").read_text())
    pro = frame(prec_list, pty, json.loads((DATA / "topic_pairs.json").read_text()))
    texts = hist["text"].tolist() + pro["text"].tolist()
    years = hist["year"].tolist() + pro["year"].tolist()
    titles = hist["title"].tolist() + pro["title"].tolist()
    retr = retrieval_features(texts, years, titles)[len(hist):]
    for k in ("ev_frame_top5_sim", "nov_nn_distance", "nov_review_overlap"):
        pro[k] = [r.get(k, np.nan) for r in retr]
    pro = pro[hist.drop(columns=[c for c in hist.columns if c not in pro.columns]).columns]
    T = fc.TARGET
    out = pro[["paper_id", "frame_topic", "cs_subfield"]].copy()
    preds = ev.predictors(hist)
    for name in ("paper3_cs_logistic", "paper3_cs_gbm", "combined_logistic", "citation_trend",
                 "publication_count", "research_trend", "simple_statistical",
                 "text_similarity_knn", "random"):
        out[name] = preds[name](hist, pro, T)
    hty = json.loads((ROOT / "data/cs_forecast/topic_years.json").read_text())
    hpost, ppost = posting(hist, hty, hrecs), posting(pro, pty, precs)
    saved = ev.BASELINE_INPUTS
    ev.BASELINE_INPUTS = {k: v for k, v in saved.items() if k != "citation_trend"}
    pp = ev.predictors(hpost)
    out["posting_paper3_cs_logistic"] = pp["paper3_cs_logistic"](hpost, ppost, T)
    out["posting_combined_logistic"] = pp["combined_logistic"](hpost, ppost, T)
    for b in ("publication_count", "research_trend", "simple_statistical"):
        out[f"posting_{b}"] = pp[b](hpost, ppost, T)
    ev.BASELINE_INPUTS = saved
    out = out.sort_values("paper_id").reset_index(drop=True)
    OUT.mkdir(parents=True, exist_ok=True)
    csv = OUT / "predictions.csv"
    out.round(10).to_csv(csv, index=False)
    sha = hashlib.sha256(csv.read_bytes()).hexdigest()
    cohort = json.loads((DATA / "cohort.json").read_text())
    (OUT / "manifest.json").write_text(json.dumps({
        "amendment": "research/preregistration_cs_breakthrough_forecast_v1_amendment8_prospective_2025.md",
        "registered_utc": datetime.now(timezone.utc).isoformat(),
        "predictions_sha256": sha, "n_papers": int(len(out)),
        "cohort": {k: cohort[k] for k in ("retrieved_utc", "filter", "seed", "candidates",
                                          "ineligible")},
        "fetch": json.loads((DATA / "fetch_manifest.json").read_text()),
        "training_papers": int(len(hist)), "evaluate_not_before": "2029-04-01",
        "outcome": "citations dated 2026-2028 to any exact-title version; top decile within cohort",
    }, indent=1) + "\n")
    print(json.dumps({"n": len(out), "sha256": sha}))


if __name__ == "__main__":
    {"sample": sample, "fetch": fetch, "predict": predict}[sys.argv[1]]()
