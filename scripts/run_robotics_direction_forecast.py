#!/usr/bin/env python3
"""Robotics research-direction growth forecast v1: fetch, rolling backtest, registration.

Frozen in research/preregistration_robotics_direction_forecast_v1.md. Reuses the CS direction
panel (scripts/run_cs_direction_forecast.py) for the transfer models and the CS normaliser.

    python3 scripts/run_robotics_direction_forecast.py fetch
    python3 scripts/run_robotics_direction_forecast.py backtest
    python3 scripts/run_robotics_direction_forecast.py register
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

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/robotics_direction_forecast"
OUT = ROOT / "results/robotics_direction_forecast_v1"
EXCLUDE = {"Robotic Process Automation Applications"}  # software automation, not robots
MIN_P, MIN_P5 = 30, 5

_s = importlib.util.spec_from_file_location("d", ROOT / "scripts/run_cs_direction_forecast.py")
d = importlib.util.module_from_spec(_s)
_s.loader.exec_module(d)
oa = d.oa
oa.CACHE, oa.MAX_REQUESTS = DATA / "cache", 300


def fetch() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    api, oa.API = oa.API, "https://api.openalex.org/topics"
    try:
        found = oa.get({"search": "robot", "per_page": 200,
                        "select": "id,display_name,subfield,field,works_count"})["data"]["results"]
    finally:
        oa.API = api
    sel = [t for t in found if "robot" in t["display_name"].lower()
           and t["display_name"] not in EXCLUDE]
    yr = "publication_year:2000-2025"
    counts = {}
    for t in sel:
        tid, fid = oa.short(t["id"]), oa.short(t["field"]["id"])
        counts[tid] = {"name": t["display_name"], "subfield": t["subfield"]["display_name"],
                       "field": t["field"]["display_name"],
                       "P": oa.group_years(f"primary_topic.id:{tid},{yr}"),
                       "A": oa.group_years(f"topics.id:{tid},{yr}"),
                       "X": oa.group_years(f"topics.id:{tid},primary_topic.field.id:!{fid},{yr}")}
    cs_total = json.loads((d.DATA / "topic_year_counts.json").read_text())["cs_total"]
    (DATA / "topic_year_counts.json").write_text(json.dumps(
        {"retrieved_utc": datetime.now(timezone.utc).isoformat(), "cs_total": cs_total,
         "search_hits": [t["display_name"] for t in found], "excluded": sorted(EXCLUDE),
         "topics": counts}, indent=1) + "\n")
    print(json.dumps({"search_hits": len(found), "selected": len(counts), **oa.STATS}))


def panel() -> pd.DataFrame:
    """Same features as the CS panel (CS-normalised), with the relaxed robotics eligibility."""
    src = json.loads((DATA / "topic_year_counts.json").read_text())
    cs = {int(k): v for k, v in src["cs_total"].items()}
    rows = []
    for tid, t in src["topics"].items():
        P = {y: t["P"].get(str(y), 0) for y in d.YEARS}
        A = {y: t["A"].get(str(y), 0) for y in d.YEARS}
        X = {y: t["X"].get(str(y), 0) for y in d.YEARS}
        rel = lambda y, k: (np.log((P[y] + 1) / (P[y - k] + 1))  # noqa: E731
                            - np.log(cs[y] / cs[y - k]))
        for o in range(d.FIRST_TRAIN, 2026):
            yearly = [rel(y, 1) for y in range(o - 4, o + 1)]
            row = {"topic": tid, "name": t["name"], "subfield": t["subfield"],
                   "field": t["field"], "origin": o, "P_o": P[o], "P_o5": P[o - 5],
                   "log_p": np.log1p(P[o]), "g1": rel(o, 1), "g3": rel(o, 3), "g5": rel(o, 5),
                   "accel": rel(o, 3) - rel(o - 3, 3), "share": P[o] / cs[o],
                   "breadth": A[o] / max(P[o], 1), "diffusion": X[o] / max(A[o], 1),
                   "d_diffusion3": X[o] / max(A[o], 1) - X[o - 3] / max(A[o - 3], 1),
                   "volatility": float(np.std(yearly))}
            if o + d.H <= 2025:
                row["G"] = rel(o + d.H, d.H)
            rows.append(row)
    df = pd.DataFrame(rows)
    return df[(df.P_o >= MIN_P) & (df.P_o5 >= MIN_P5)].reset_index(drop=True)


def scorers(cs: pd.DataFrame):
    fit = lambda src, kind: (lambda tr, te, t: d.model(kind).fit(  # noqa: E731
        src(tr, t)[d.FEATS], src(tr, t).G).predict(te[d.FEATS]))
    cs_src = lambda tr, t: cs[(cs.origin <= t - d.H) & cs.G.notna()]  # noqa: E731
    rb_src = lambda tr, t: tr  # noqa: E731
    return {"g1": lambda tr, te, t: te.g1.to_numpy(), "g3": lambda tr, te, t: te.g3.to_numpy(),
            "g5": lambda tr, te, t: te.g5.to_numpy(),
            "ridge_transfer_cs": fit(cs_src, "ridge"), "gbm_transfer_cs": fit(cs_src, "gbm"),
            "ridge_robotics": fit(rb_src, "ridge")}


def mean_rho(pred: pd.DataFrame, n: str) -> float:
    return float(np.nanmean([spearmanr(g[n], g.G).statistic if g[n].std() > 0 else np.nan
                             for _, g in pred.groupby("origin")]))


def backtest() -> None:
    df, cs = panel(), d.panel()
    sc, blocks = scorers(cs), []
    for t in d.TEST_ORIGINS:
        tr = df[(df.origin <= t - d.H) & df.G.notna()]
        te = df[(df.origin == t) & df.G.notna()].copy()
        for n, f in sc.items():
            te[n] = f(tr, te, t)
        blocks.append(te)
    pred = pd.concat(blocks, ignore_index=True)
    names = list(sc)
    point = {n: mean_rho(pred, n) for n in names}
    best = max(["g1", "g3", "g5"], key=lambda b: point[b])
    rng = np.random.default_rng(d.SEED)
    topics = pred.topic.unique()
    idx = {k: np.where(pred.topic.to_numpy() == k)[0] for k in topics}
    boot, diff = {n: [] for n in names}, {n: [] for n in names}
    for _ in range(d.REPS):
        x = pred.iloc[np.concatenate([idx[k] for k in rng.choice(topics, len(topics))])]
        r = {n: mean_rho(x, n) for n in names}
        for n in names:
            boot[n].append(r[n])
            diff[n].append(r[n] - r[best])
    ci = lambda v: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]  # noqa: E731
    per = {int(t): {"n": int(len(g)), **{n: float(spearmanr(g[n], g.G).statistic) for n in names}}
           for t, g in pred.groupby("origin")}
    out = {"preregistration": "research/preregistration_robotics_direction_forecast_v1.md",
           "n_rows": int(len(pred)), "n_topics": int(len(topics)),
           "mean_spearman": point, "mean_spearman_ci95": {n: ci(boot[n]) for n in names},
           "best_momentum_baseline": best,
           "delta_vs_best_ci95": {n: ci(diff[n]) for n in names}, "per_origin": per}
    out["gates"] = {"R1_best_momentum_lower_gt_0": out["mean_spearman_ci95"][best][0] > 0,
                    "R2_ridge_transfer_cs_minus_best_lower_gt_0":
                        out["delta_vs_best_ci95"]["ridge_transfer_cs"][0] > 0,
                    "R3_ridge_robotics_minus_best_lower_gt_0":
                        out["delta_vs_best_ci95"]["ridge_robotics"][0] > 0}
    OUT.mkdir(parents=True, exist_ok=True)
    pred.to_csv(OUT / "backtest_predictions.csv", index=False)
    (OUT / "backtest.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(json.dumps({k: out[k] for k in ("n_rows", "n_topics", "mean_spearman",
                                          "mean_spearman_ci95", "best_momentum_baseline",
                                          "delta_vs_best_ci95", "gates")}, indent=1, default=float))


def register() -> None:
    df, cs = panel(), d.panel()
    sc = scorers(cs)
    tr = df[(df.origin <= 2020) & df.G.notna()]
    te = df[df.origin == 2025].copy()
    for n, f in sc.items():
        te[n] = f(tr, te, 2025)
        te[f"rank_{n}"] = te[n].rank(ascending=False, method="min").astype(int)
    out = te.drop(columns=["G"], errors="ignore").sort_values("rank_ridge_transfer_cs")
    OUT.mkdir(parents=True, exist_ok=True)
    csv = OUT / "prospective_2030.csv"
    out.round(8).to_csv(csv, index=False)
    sha = hashlib.sha256(csv.read_bytes()).hexdigest()
    (OUT / "prospective_manifest.json").write_text(json.dumps({
        "registered_utc": datetime.now(timezone.utc).isoformat(), "sha256": sha, "origin": 2025,
        "n_topics": int(len(out)), "primary_ranking": "ridge_transfer_cs",
        "target": "CS-normalised log growth of primary-topic works, 2025 -> 2030 (Spearman)",
        "evaluate_not_before": "2031-06-01",
        "caveat": "ranking of existing robotics directions by forecast growth; not breakthroughs"},
        indent=1) + "\n")
    print(json.dumps({"sha256": sha, "n_topics": int(len(out))}))


if __name__ == "__main__":
    {"fetch": fetch, "backtest": backtest, "register": register}[sys.argv[1]]()
