#!/usr/bin/env python3
"""Literature-derived direction features beyond momentum: fetch, discovery, confirmation, register.

Frozen in research/preregistration_cs_direction_features_v2.md. Reuses the CS direction panel.

    python3 scripts/run_cs_direction_features_v2.py fetch
    python3 scripts/run_cs_direction_features_v2.py discover
    python3 scripts/run_cs_direction_features_v2.py confirm
    python3 scripts/run_cs_direction_features_v2.py register
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
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/cs_direction_features_v2"
OUT = ROOT / "results/cs_direction_features_v2"
DEV, CONF = range(2011, 2016), range(2016, 2020)
SUB = {"ml": "keywords.id:machine-learning", "dl": "keywords.id:deep-learning",
       "llm": "keywords.id:large-language-models",
       "company": "authorships.institutions.type:company",
       "arxiv": "locations.source.id:S4306400194", "cn": "authorships.countries:CN",
       "us": "authorships.countries:US", "conf": "primary_location.source.type:conference"}
BACKTEST_SUB = [k for k in SUB if k != "llm"]  # llm is ~0 before 2020: descriptive only
CANDIDATES = [f"{p}_{k}" for k in BACKTEST_SUB for p in ("share", "d3share")]

_s = importlib.util.spec_from_file_location("d", ROOT / "scripts/run_cs_direction_forecast.py")
d = importlib.util.module_from_spec(_s)
_s.loader.exec_module(d)
oa = d.oa
oa.CACHE, oa.MAX_REQUESTS = DATA / "cache", 3000


def fetch() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    topics = json.loads((d.DATA / "topic_year_counts.json").read_text())["topics"]
    yr = "publication_year:2000-2025"
    out = {tid: {k: oa.group_years(f"primary_topic.id:{tid},{f},{yr}") for k, f in SUB.items()}
           for tid in topics}
    (DATA / "feature_counts.json").write_text(json.dumps(
        {"retrieved_utc": datetime.now(timezone.utc).isoformat(), "filters": SUB,
         "topics": out}, indent=1) + "\n")
    print(json.dumps({"topics": len(out), **oa.STATS}))


def panel() -> pd.DataFrame:
    base = d.panel()
    src = json.loads((d.DATA / "topic_year_counts.json").read_text())["topics"]
    sub = json.loads((DATA / "feature_counts.json").read_text())["topics"]
    share = lambda tid, k, y: (sub[tid][k].get(str(y), 0)  # noqa: E731
                               / max(src[tid]["P"].get(str(y), 0), 1))
    for k in SUB:
        base[f"share_{k}"] = [share(t, k, o) for t, o in zip(base.topic, base.origin)]
        base[f"d3share_{k}"] = base[f"share_{k}"] - [share(t, k, o - 3)
                                                     for t, o in zip(base.topic, base.origin)]
    return base


def resid(g: pd.DataFrame, col: str) -> np.ndarray:
    X = np.column_stack([np.ones(len(g))] + [g[m].to_numpy() for m in d.MOMENTUM])
    y = g[col].to_numpy()
    return y - X @ np.linalg.lstsq(X, y, rcond=None)[0]


def partial_rho(df: pd.DataFrame, f: str) -> list[float]:
    out = []
    for _, g in df.groupby("origin"):
        rf = resid(g, f)
        out.append(float(spearmanr(rf, resid(g, "G")).statistic) if rf.std() > 1e-12 else np.nan)
    return out


def boot_partial(df: pd.DataFrame, feats: list[str], seed_offset: int = 0) -> dict:
    rng = np.random.default_rng(d.SEED + seed_offset)
    topics = df.topic.unique()
    idx = {k: np.where(df.topic.to_numpy() == k)[0] for k in topics}
    reps = {f: [] for f in feats}
    for _ in range(d.REPS):
        x = df.iloc[np.concatenate([idx[k] for k in rng.choice(topics, len(topics))])]
        for f in feats:
            reps[f].append(np.nanmean(partial_rho(x, f)))
    res = {}
    for f in feats:
        per = partial_rho(df, f)
        res[f] = {"mean": float(np.nanmean(per)), "per_origin": per,
                  "ci95": [float(np.nanpercentile(reps[f], 2.5)),
                           float(np.nanpercentile(reps[f], 97.5))],
                  "ci_bonferroni": [float(np.nanpercentile(reps[f], 2.5 / len(feats))),
                                    float(np.nanpercentile(reps[f], 100 - 2.5 / len(feats)))]}
    return res


def discover() -> None:
    df = panel()
    dev = df[df.origin.isin(DEV) & df.G.notna()]
    res = boot_partial(dev, CANDIDATES)
    selected = {}
    for f, r in res.items():
        sign = np.sign(r["mean"])
        agree = sum(np.sign(v) == sign for v in r["per_origin"] if not np.isnan(v))
        r["sign_agree_origins"] = int(agree)
        if (r["ci95"][0] > 0 or r["ci95"][1] < 0) and agree >= 4:
            selected[f] = int(sign)
    OUT.mkdir(parents=True, exist_ok=True)
    out = {"preregistration": "research/preregistration_cs_direction_features_v2.md",
           "dev_origins": list(DEV), "n_rows": int(len(dev)), "candidates": res,
           "selected": selected}
    (OUT / "discovery.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(json.dumps({"n_rows": out["n_rows"], "selected": selected,
                      "summary": {f: [round(r["mean"], 3), [round(c, 3) for c in r["ci95"]],
                                      r["sign_agree_origins"]] for f, r in res.items()}},
                     indent=1))


def _fit_predict(tr, te, cols):
    return d.model("ridge").fit(tr[cols], tr.G).predict(te[cols])


def confirm() -> None:
    sel = json.loads((OUT / "discovery.json").read_text())["selected"]
    if not sel:
        print("no feature selected in discovery: confirmation not run (null result)")
        return
    df = panel()
    specs = {"M0_momentum": d.MOMENTUM, "M1_momentum_plus_selected": d.MOMENTUM + list(sel),
             "ridge_all_v1": d.FEATS, "ridge_all_v1_plus_selected": d.FEATS + list(sel)}
    blocks = []
    for t in CONF:
        tr = df[(df.origin <= t - d.H) & df.G.notna()]
        te = df[(df.origin == t) & df.G.notna()].copy()
        te["y"] = (te.G >= te.G.quantile(0.9)).astype(int)
        te["g3_raw"] = te.g3
        for n, cols in specs.items():
            te[n] = _fit_predict(tr, te, cols)
        blocks.append(te)
    pred = pd.concat(blocks, ignore_index=True)
    names = ["g3_raw"] + list(specs)
    rho = lambda x, n: float(np.mean([spearmanr(g[n], g.G).statistic  # noqa: E731
                                      for _, g in x.groupby("origin")]))
    auc = lambda x, n: roc_auc_score(x.y, x[n])  # noqa: E731
    point = {n: {"spearman": rho(pred, n), "auroc": auc(pred, n)} for n in names}
    rng = np.random.default_rng(d.SEED)
    topics = pred.topic.unique()
    idx = {k: np.where(pred.topic.to_numpy() == k)[0] for k in topics}
    ds, da = {n: [] for n in names}, {n: [] for n in names}
    bs, ba = {n: [] for n in names}, {n: [] for n in names}
    for _ in range(d.REPS):
        x = pred.iloc[np.concatenate([idx[k] for k in rng.choice(topics, len(topics))])]
        r = {n: rho(x, n) for n in names}
        a = {n: auc(x, n) for n in names}
        for n in names:
            bs[n].append(r[n]); ba[n].append(a[n])
            ds[n].append(r[n] - r["M0_momentum"]); da[n].append(a[n] - a["M0_momentum"])
    ci = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]  # noqa: E731
    partial = boot_partial(pred, list(sel), seed_offset=1)
    gates = {"C1_spearman_M1_minus_M0_lower_gt_0": ci(ds["M1_momentum_plus_selected"])[0] > 0,
             "C2_auroc_M1_minus_M0_lower_gt_0": ci(da["M1_momentum_plus_selected"])[0] > 0,
             "C3_selected_partial_replicates": {
                 f: (partial[f]["ci95"][0] > 0) if s > 0 else (partial[f]["ci95"][1] < 0)
                 for f, s in sel.items()}}
    out = {"preregistration": "research/preregistration_cs_direction_features_v2.md",
           "confirm_origins": list(CONF), "selected": sel, "n_rows": int(len(pred)),
           "point": point, "spearman_ci95": {n: ci(bs[n]) for n in names},
           "auroc_ci95": {n: ci(ba[n]) for n in names},
           "delta_vs_M0_spearman_ci95": {n: ci(ds[n]) for n in names},
           "delta_vs_M0_auroc_ci95": {n: ci(da[n]) for n in names},
           "confirm_partial": partial, "gates": gates}
    pred.to_csv(OUT / "confirmation_predictions.csv", index=False)
    (OUT / "confirmation.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(json.dumps({k: out[k] for k in ("n_rows", "point", "delta_vs_M0_spearman_ci95",
                                          "delta_vs_M0_auroc_ci95", "gates")}, indent=1,
                     default=float))


def register() -> None:
    df = panel()
    conf = OUT / "confirmation.json"
    passed = conf.exists() and json.loads(conf.read_text())["gates"][
        "C1_spearman_M1_minus_M0_lower_gt_0"]
    te = df[df.origin == 2025].copy()
    cols = ["topic", "name", "subfield", "P_o", "g3"] + [f"share_{k}" for k in SUB] + \
           [f"d3share_{k}" for k in SUB]
    if passed:
        sel = json.loads(conf.read_text())["selected"]
        tr = df[(df.origin <= 2020) & df.G.notna()]
        te["M1_score"] = _fit_predict(tr, te, d.MOMENTUM + list(sel))
        te["rank_M1"] = te.M1_score.rank(ascending=False, method="min").astype(int)
        cols += ["M1_score", "rank_M1"]
        name = "prospective_2030_M1.csv"
    else:
        name = "descriptive_2025_features.csv"  # no confirmed model: descriptive only
    csv = OUT / name
    te.sort_values("rank_M1" if passed else "g3", ascending=passed)[cols].round(8).to_csv(
        csv, index=False)
    sha = hashlib.sha256(csv.read_bytes()).hexdigest()
    (OUT / "register_manifest.json").write_text(json.dumps({
        "registered_utc": datetime.now(timezone.utc).isoformat(), "csv": name, "sha256": sha,
        "confirmed_model": bool(passed), "evaluate_not_before": "2031-06-01" if passed else None},
        indent=1) + "\n")
    print(json.dumps({"csv": name, "sha256": sha, "confirmed_model": bool(passed)}))


if __name__ == "__main__":
    {"fetch": fetch, "discover": discover, "confirm": confirm, "register": register}[sys.argv[1]]()
