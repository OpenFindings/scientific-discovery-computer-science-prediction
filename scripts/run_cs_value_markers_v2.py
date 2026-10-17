#!/usr/bin/env python3
"""Expanded documentary value-marker study (amendment 6): sample, prompts, ingest, verify, analyze.

Frozen in research/preregistration_cs_breakthrough_forecast_v1_amendment6_value_markers_v2.md.
Reuses amendment 5's verifier and audit. Searching is done by fresh subagents.

    python3 scripts/run_cs_value_markers_v2.py sample
    python3 scripts/run_cs_value_markers_v2.py prompt <batch>
    python3 scripts/run_cs_value_markers_v2.py ingest <batch> <transcript.jsonl> <prompt_file>
    python3 scripts/run_cs_value_markers_v2.py verify
    python3 scripts/run_cs_value_markers_v2.py analyze
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results/cs_forecast_v1"
SAMPLE = RES / "value_sample_v2.json"  # items + hidden strata (searchers never see this file)
RAW = RES / "value_markers_v2_raw.jsonl"
VER = RES / "value_markers_v2_verified.json"
BATCH, SEED = 20, 20261018
R_TOTAL, M_TOTAL = 200, 100

_s = importlib.util.spec_from_file_location("v1", ROOT / "scripts/run_cs_value_markers.py")
v1 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(v1)

EXTRA = """
Search effort: run at least two separate web searches per paper (for example the title, and the
method or dataset name with words like "survey", "library", "course" or "award") before
concluding that no evidence exists. Add a field "searches": <number of web searches you ran for
that paper> to each object.
"""


def sample() -> None:
    f = pd.read_csv(RES / "features.csv", dtype={"paper_id": str})
    p = pd.read_csv(RES / "predictions_primary.csv", dtype={"paper_id": str})
    snap = {json.loads(l)["paper_id"]: json.loads(l)
            for l in open(ROOT / "data/cs_forecast/snapshot_v1.jsonl")}
    old = json.loads((RES / "labeling_key.json").read_text())["strata"]
    df = f[["paper_id", "year", "y_breakthrough"]].merge(
        p[["paper_id", "paper3_cs_logistic"]], on="paper_id", how="left")
    t_new = df[(df.y_breakthrough == 1) & ~df.paper_id.isin(old)]
    neg = df[df.y_breakthrough == 0]
    top = neg[neg.paper3_cs_logistic.notna()].sort_values("paper3_cs_logistic",
                                                          ascending=False).head(M_TOTAL)
    m_new = top[~top.paper_id.isin(old)]
    rest = neg[~neg.paper_id.isin(top.paper_id) & ~neg.paper_id.isin(old)]
    n_r = R_TOTAL - sum(v == "random_citation_negative" for v in old.values())
    r_new = rest.sample(n_r, random_state=SEED)
    key = ([(x, "citation_top_decile") for x in t_new.paper_id]
           + [(x, "model_high_citation_negative") for x in m_new.paper_id]
           + [(x, "random_citation_negative") for x in r_new.paper_id])
    order = np.random.default_rng(SEED).permutation(len(key))
    items = [{"id": key[i][0], "year": int(snap[key[i][0]]["year"]),
              "title": snap[key[i][0]]["title"]} for i in order]
    SAMPLE.write_text(json.dumps({"seed": SEED, "items": items,
                                  "strata": {pid: st for pid, st in key}}, indent=1) + "\n")
    print(Counter(st for _, st in key), len(items), "batches", -(-len(items) // BATCH))


def items() -> list[dict]:
    return json.loads(SAMPLE.read_text())["items"]


# addendum 1: items whose first search was cut short by the shared web-search budget
SUPPLEMENT = [41, 42, 46, 47, 50, 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 69, 70,
              71, 74, 75, 76, 77, 78, 79, 80, 81, 83, 84, 85, 86, 87, 88, 89, 91, 93, 94, 95, 121,
              123, 125, 126, 127, 128, 129, 130, 131, 132, 135, 136, 137, 138, 139, 140,
              4, 11, 15, 20]  # last 4: batch 1, screened after its late hand-back


def batch_items(b: int) -> list[tuple[int, dict]]:
    its = items()
    if b >= 101:  # supplementary batches 101-104 (20, 20, 20, 2 items)
        chunk = SUPPLEMENT[(b - 101) * BATCH:(b - 100) * BATCH]
        return [(n, its[n - 1]) for n in chunk]
    lo = (b - 1) * BATCH
    return [(i + 1, its[i]) for i in range(lo, min(lo + BATCH, len(its)))]


def prompt(b: int) -> str:
    head = v1.INSTRUCTIONS.replace(
        '"notes": "<at most 40 words>"}', '"notes": "<at most 40 words>", "searches": <n>}')
    head = head.replace("\nPapers:\n", EXTRA + "\nPapers:\n")
    lines = [head] + [f'Item {n}: arXiv {it["id"]}, {it["year"]}, "{it["title"]}"'
                      for n, it in batch_items(b)]
    return "\n".join(lines) + "\n"


def ingest(b: int, transcript: str, prompt_file: str) -> None:
    v1.RAW, v1.batch_items = RAW, batch_items  # reuse amendment 5's audit and parsing
    v1.ingest(b, transcript, prompt_file)


def accepted() -> dict[str, dict]:
    its, out = items(), {}
    for line in RAW.read_text().splitlines():
        rec = json.loads(line)
        if rec["accepted"]:
            arr = json.loads(rec["reply"][rec["reply"].find("["): rec["reply"].rfind("]") + 1])
            for o in arr:
                pid = its[o["item"] - 1]["id"]
                if pid in out:  # addendum 1: union of claims, max reported searches
                    prev = out[pid]
                    o = {**o, "markers": (prev.get("markers") or []) + (o.get("markers") or []),
                         "searches": max(prev.get("searches") or 0, o.get("searches") or 0),
                         "notes": f'{prev.get("notes")} || {o.get("notes")}'}
                out[pid] = o
    return out


def verify() -> None:
    acc, its = accepted(), {it["id"]: it for it in items()}
    cache, out = {}, {}
    for pid, o in acc.items():
        res = []
        for m in o.get("markers") or []:
            url, quote = m.get("url", ""), m.get("quote", "")
            host = urlparse(url).netloc.lower() + urlparse(url).path.lower()
            if any(h in host for h in v1.EXCLUDED_HOSTS):
                st = "excluded_source"
            else:
                if url not in cache:
                    try:
                        cache[url] = v1.fetch(url)
                    except Exception:
                        cache[url] = (0, "")
                    time.sleep(1)
                code, text = cache[url]
                if code >= 400 or code == 0 or not text.strip():
                    st = "fetch_failed"
                elif v1.normalize(quote) not in v1.normalize(text):
                    st = "quote_not_found"
                elif not v1.names_paper(text, pid, its[pid]["title"]):
                    st = "paper_not_named"
                else:
                    st = "verified"
            res.append({**m, "status": st})
        out[pid] = {"markers": res, "searches": o.get("searches"), "notes": o.get("notes")}
    VER.write_text(json.dumps({"verified_at": datetime.now(timezone.utc).isoformat(),
                               "papers": out}, indent=1) + "\n")
    print(Counter(m["status"] for v in out.values() for m in v["markers"]))


def analyze() -> None:
    rows = []
    s1 = json.loads((RES / "labeling_key.json").read_text())["strata"]
    ver1 = json.loads((RES / "value_markers_verified.json").read_text())["papers"]
    for pid, ms in ver1.items():
        ok = {m["type"] for m in ms if m["status"] == "verified"}
        rows.append({"paper_id": pid, "stratum": s1[pid], "wave": 1, "types": ok, "searches": None})
    s2 = json.loads(SAMPLE.read_text())["strata"]
    ver2 = json.loads(VER.read_text())["papers"]
    for pid, o in ver2.items():
        ok = {m["type"] for m in o["markers"] if m["status"] == "verified"}
        rows.append({"paper_id": pid, "stratum": s2[pid], "wave": 2, "types": ok,
                     "searches": o.get("searches")})
    for r in rows:
        r["V"] = int(bool(r["types"] & {"M1", "M2", "M3"}))
        r["V4"] = int(bool(r["types"]))
        r["types"] = sorted(r["types"])
    inv = {v: k for k, v in v1.NAMES.items()}
    rng = np.random.default_rng(v1.SEED)

    def grp(s, k, wave=None):
        return [r[k] for r in rows if inv[r["stratum"]] == s and (wave is None or r["wave"] == wave)]

    c1 = v1.rd(grp("T", "V"), grp("R", "V"), rng)
    c2 = v1.rd(grp("M", "V"), grp("R", "V"), rng)
    verdict1 = ("citation_label_agrees_with_documentary_value" if c1["rd_ci95"][0] > 0 else
                "citation_label_does_not_agree" if c1["rd_ci95"][1] < 0.10 else "inconclusive")
    verdict2 = "structure_model_finds_value_citations_miss" if c2["rd_ci95"][0] > 0 else "no_evidence"

    # C3: model score predicts V among searched citation negatives with a model score
    pred = pd.read_csv(RES / "predictions_primary.csv", dtype={"paper_id": str})
    sc = dict(zip(pred.paper_id, pred.paper3_cs_logistic))
    neg = [(sc[r["paper_id"]], r["V"]) for r in rows
           if inv[r["stratum"]] != "T" and r["paper_id"] in sc and not np.isnan(sc[r["paper_id"]])]
    x, y = np.array([a for a, _ in neg]), np.array([b for _, b in neg])
    if 0 < y.sum() < len(y):
        boots = []
        for _ in range(v1.REPS):
            i = rng.integers(0, len(y), len(y))
            if 0 < y[i].sum() < len(y):
                boots.append(roc_auc_score(y[i], x[i]))
        c3 = {"n": int(len(y)), "positives": int(y.sum()), "auroc": float(roc_auc_score(y, x)),
              "auroc_ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]}
        c3["verdict"] = "model_score_predicts_value" if c3["auroc_ci95"][0] > 0.5 else "no_evidence"
    else:
        c3 = {"n": int(len(y)), "positives": int(y.sum()), "note": "no variation in V"}
    out = {
        "amendment": "research/preregistration_cs_breakthrough_forecast_v1_amendment6_value_markers_v2.md",
        "n_by_stratum_wave": dict(Counter(f"{inv[r['stratum']]}_w{r['wave']}" for r in rows)),
        "verification_status_wave2": dict(Counter(m["status"] for v in ver2.values()
                                                  for m in v["markers"])),
        "verified_types_by_stratum": {s: dict(Counter(t for r in rows if inv[r["stratum"]] == s
                                                      for t in r["types"])) for s in v1.NAMES},
        "C1_T_vs_R_V_pooled": c1, "C1_verdict": verdict1,
        "C2_M_vs_R_V_pooled": c2, "C2_verdict": verdict2,
        "C3_model_score_auroc_for_V_among_negatives": c3,
        "C4": {"T_vs_R_V4_pooled": v1.rd(grp("T", "V4"), grp("R", "V4"), rng),
               "M_vs_R_V4_pooled": v1.rd(grp("M", "V4"), grp("R", "V4"), rng),
               "T_vs_R_V_wave2_only": v1.rd(grp("T", "V", 2), grp("R", "V", 2), rng),
               "M_vs_R_V_wave2_only": v1.rd(grp("M", "V", 2), grp("R", "V", 2), rng)},
        "C5_reported_searches_wave2": {s: {"mean": float(np.mean([v for v in grp(s, "searches", 2)
                                                                   if isinstance(v, (int, float))]))
                                           if any(isinstance(v, (int, float))
                                                  for v in grp(s, "searches", 2)) else None}
                                       for s in v1.NAMES},
        "rows": rows, "seed": v1.SEED, "reps": v1.REPS}
    (RES / "value_markers_v2_analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("n_by_stratum_wave", "verification_status_wave2",
                                          "C1_verdict", "C2_verdict")}, indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sample":
        sample()
    elif cmd == "prompt":
        print(prompt(int(sys.argv[2])), end="")
    elif cmd == "ingest":
        ingest(int(sys.argv[2]), sys.argv[3], sys.argv[4])
    elif cmd == "verify":
        verify()
    else:
        analyze()
