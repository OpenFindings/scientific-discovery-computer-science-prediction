#!/usr/bin/env python3
"""CS research-direction growth forecast v1: fetch, rolling backtest, prospective registration.

Frozen in research/preregistration_cs_direction_forecast_v1.md.

    python3 scripts/run_cs_direction_forecast.py fetch
    python3 scripts/run_cs_direction_forecast.py backtest
    python3 scripts/run_cs_direction_forecast.py register
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/cs_direction_forecast"
OUT = ROOT / "results/cs_direction_forecast_v1"
YEARS = range(2000, 2026)
TEST_ORIGINS = range(2011, 2020)
FIRST_TRAIN, H, SEED, REPS = 2006, 5, 20261017, 2000
FEATS = ["log_p", "g1", "g3", "g5", "accel", "share", "breadth", "diffusion", "d_diffusion3",
         "volatility"]
MOMENTUM = ["g1", "g3", "g5", "accel"]

_s = importlib.util.spec_from_file_location("oa", ROOT / "scripts/fetch_openalex_frame.py")
oa = importlib.util.module_from_spec(_s)
_s.loader.exec_module(oa)
oa.API = "https://api.openalex.org/works"
oa.CACHE, oa.MAX_REQUESTS = DATA / "cache", 1000


def topics_get(page: int) -> dict:
    api, oa.API = oa.API, "https://api.openalex.org/topics"
    try:
        return oa.get({"filter": "field.id:17", "per_page": 200, "page": page,
                       "select": "id,display_name,subfield,works_count"})
    finally:
        oa.API = api


def fetch() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    topics = []
    for page in (1, 2):
        topics += topics_get(page)["data"]["results"]
    yr = "publication_year:2000-2025"
    cs_total = oa.group_years(f"primary_topic.field.id:17,{yr}")
    counts = {}
    for t in topics:
        tid = oa.short(t["id"])
        counts[tid] = {"name": t["display_name"], "subfield": t["subfield"]["display_name"],
                       "P": oa.group_years(f"primary_topic.id:{tid},{yr}"),
                       "A": oa.group_years(f"topics.id:{tid},{yr}"),
                       "X": oa.group_years(f"topics.id:{tid},primary_topic.field.id:!17,{yr}")}
    (DATA / "topic_year_counts.json").write_text(json.dumps(
        {"retrieved_utc": datetime.now(timezone.utc).isoformat(), "cs_total": cs_total,
         "topics": counts}, indent=1) + "\n")
    print(json.dumps({"topics": len(counts), **oa.STATS}))


def panel() -> pd.DataFrame:
    d = json.loads((DATA / "topic_year_counts.json").read_text())
    cs = {int(k): v for k, v in d["cs_total"].items()}
    rows = []
    for tid, t in d["topics"].items():
        P = {y: t["P"].get(str(y), 0) for y in YEARS}
        A = {y: t["A"].get(str(y), 0) for y in YEARS}
        X = {y: t["X"].get(str(y), 0) for y in YEARS}
        rel = lambda y, k: (np.log((P[y] + 1) / (P[y - k] + 1))  # noqa: E731
                            - np.log(cs[y] / cs[y - k]))
        for o in range(FIRST_TRAIN, 2026):
            if o - 8 < 2000:
                continue
            yearly = [rel(y, 1) for y in range(o - 4, o + 1)]
            row = {"topic": tid, "name": t["name"], "subfield": t["subfield"], "origin": o,
                   "P_o": P[o], "P_o5": P[o - 5],
                   "log_p": np.log1p(P[o]), "g1": rel(o, 1), "g3": rel(o, 3), "g5": rel(o, 5),
                   "accel": rel(o, 3) - rel(o - 3, 3), "share": P[o] / cs[o],
                   "breadth": A[o] / max(P[o], 1),
                   "diffusion": X[o] / max(A[o], 1),
                   "d_diffusion3": X[o] / max(A[o], 1) - X[o - 3] / max(A[o - 3], 1),
                   "volatility": float(np.std(yearly))}
            if o + H <= 2025:
                row["G"] = rel(o + H, H)
            rows.append(row)
    df = pd.DataFrame(rows)
    return df[(df.P_o >= 100) & (df.P_o5 >= 20)].reset_index(drop=True)


def model(kind: str):
    if kind == "ridge":
        return Pipeline([("i", SimpleImputer(strategy="median")), ("s", StandardScaler()),
                         ("m", Ridge(alpha=1.0))])
    return Pipeline([("i", SimpleImputer(strategy="median")),
                     ("m", GradientBoostingRegressor(n_estimators=300, max_depth=3,
                                                     learning_rate=0.05, random_state=7))])


def scorers():
    nomo = [f for f in FEATS if f not in MOMENTUM]
    fit = lambda cols, kind: (lambda tr, te: model(kind).fit(tr[cols], tr.G).predict(te[cols]))  # noqa: E731
    return {"random": lambda tr, te: np.zeros(len(te)),
            "g1": lambda tr, te: te.g1.to_numpy(), "g3": lambda tr, te: te.g3.to_numpy(),
            "g5": lambda tr, te: te.g5.to_numpy(),
            "ridge_all": fit(FEATS, "ridge"), "gbm_all": fit(FEATS, "gbm"),
            "ridge_nomomentum": fit(nomo, "ridge")}


def backtest() -> None:
    df = panel()
    sc, blocks = scorers(), []
    for t in TEST_ORIGINS:
        tr = df[(df.origin <= t - H) & df.G.notna()]
        te = df[(df.origin == t) & df.G.notna()].copy()
        te["y"] = (te.G >= te.G.quantile(0.9)).astype(int)
        for n, f in sc.items():
            te[n] = f(tr, te)
        blocks.append(te)
    pred = pd.concat(blocks, ignore_index=True)
    names = list(sc)
    rng = np.random.default_rng(SEED)
    topics = pred.topic.unique()
    idx = {k: np.where(pred.topic.to_numpy() == k)[0] for k in topics}
    auc = lambda d, n: roc_auc_score(d.y, d[n]) if d.y.nunique() == 2 else np.nan  # noqa: E731
    point = {n: auc(pred, n) for n in names}
    best = max(["g1", "g3", "g5"], key=lambda b: point[b])
    boot = {n: [] for n in names}
    diff = {n: [] for n in names}
    for _ in range(REPS):
        d = pred.iloc[np.concatenate([idx[k] for k in rng.choice(topics, len(topics))])]
        a = {n: auc(d, n) for n in names}
        for n in names:
            boot[n].append(a[n])
            diff[n].append(a[n] - a[best])
    ci = lambda v: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]  # noqa: E731
    k = lambda g: max(1, int(round(0.1 * len(g))))  # noqa: E731
    prec = {n: float(np.mean([g.nlargest(k(g), n).y.mean() for _, g in pred.groupby("origin")]))
            for n in names}
    per_origin = {int(t): {n: {"auroc": auc(g, n), "spearman": float(spearmanr(g[n], g.G).statistic)
                               if g[n].std() > 0 else None} for n in names}
                  for t, g in pred.groupby("origin")}
    out = {"preregistration": "research/preregistration_cs_direction_forecast_v1.md",
           "n_rows": int(len(pred)), "n_topics": int(len(topics)),
           "auroc": point, "auroc_ci95": {n: ci(boot[n]) for n in names},
           "best_momentum_baseline": best,
           "delta_vs_best_ci95": {n: ci(diff[n]) for n in names}, "precision_top10": prec,
           "per_origin": per_origin}
    out["gates"] = {"F1_ridge_all_lower_gt_0.5": out["auroc_ci95"]["ridge_all"][0] > 0.5,
                    "F2_ridge_all_minus_best_momentum_lower_gt_0":
                        out["delta_vs_best_ci95"]["ridge_all"][0] > 0,
                    "F3_ridge_nomomentum_lower_gt_0.5": out["auroc_ci95"]["ridge_nomomentum"][0] > 0.5}
    OUT.mkdir(parents=True, exist_ok=True)
    pred.to_csv(OUT / "backtest_predictions.csv", index=False)
    (OUT / "backtest.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(json.dumps({k2: out[k2] for k2 in ("n_rows", "n_topics", "auroc", "auroc_ci95",
                                             "best_momentum_baseline", "gates")}, indent=1,
                     default=float))


def register() -> None:
    df = panel()
    d = json.loads((DATA / "topic_year_counts.json").read_text())
    ratio = d["cs_total"]["2025"] / d["cs_total"]["2024"]
    origins = [2025] + ([2024] if ratio < 0.9 else [])
    sc, frames = scorers(), []
    for o in origins:
        tr = df[(df.origin <= o - H) & df.G.notna()]
        te = df[df.origin == o].copy()
        for n, f in sc.items():
            if n != "random":
                te[n] = f(tr, te)
                te[f"rank_{n}"] = te[n].rank(ascending=False, method="min").astype(int)
        frames.append(te)
    out = pd.concat(frames).drop(columns=["G"], errors="ignore").sort_values(
        ["origin", "rank_ridge_all"])
    OUT.mkdir(parents=True, exist_ok=True)
    csv = OUT / "prospective_2030.csv"
    out.round(8).to_csv(csv, index=False)
    sha = hashlib.sha256(csv.read_bytes()).hexdigest()
    (OUT / "prospective_manifest.json").write_text(json.dumps({
        "registered_utc": datetime.now(timezone.utc).isoformat(), "sha256": sha,
        "origins": origins, "cs_2025_over_2024": ratio, "n_topics": int((out.origin == 2025).sum()),
        "target": "CS-relative log growth of primary-topic works, origin -> origin+5",
        "evaluate_not_before": "2031-06-01",
        "caveat": "ranking of existing directions by forecast relative growth; not breakthroughs"},
        indent=1) + "\n")
    print(json.dumps({"sha256": sha, "origins": origins, "ratio_2025_2024": ratio}))


if __name__ == "__main__":
    {"fetch": fetch, "backtest": backtest, "register": register}[sys.argv[1]]()
