#!/usr/bin/env python3
"""Surprise-riser forecast (growth beyond momentum) for CS directions.

Frozen in research/preregistration_cs_direction_surprise_v1.md. Reuses the direction panel.

    python3 scripts/run_cs_direction_surprise.py
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/cs_direction_forecast_v1"
_s = importlib.util.spec_from_file_location("d", ROOT / "scripts/run_cs_direction_forecast.py")
d = importlib.util.module_from_spec(_s)
_s.loader.exec_module(d)
SINGLE = {"accel": 1, "d_diffusion3": 1, "diffusion": 1, "volatility": 1, "log_p": -1, "g3": 1}


def residualize(tr, te):
    lm = LinearRegression().fit(tr[["g3"]], tr.G)
    return tr.G - lm.predict(tr[["g3"]]), te.G - lm.predict(te[["g3"]]) if "G" in te else None, lm


def main() -> None:
    df = d.panel()
    nomo = [f for f in d.FEATS if f not in d.MOMENTUM]
    blocks = []
    for t in d.TEST_ORIGINS:
        tr = df[(df.origin <= t - d.H) & df.G.notna()].copy()
        te = df[(df.origin == t) & df.G.notna()].copy()
        tr["S"], te["S"], _ = residualize(tr, te)
        te["y"] = (te.S >= te.S.quantile(0.9)).astype(int)
        te["ridge_resid_all"] = d.model("ridge").fit(tr[d.FEATS], tr.S).predict(te[d.FEATS])
        te["ridge_resid_nomomentum"] = d.model("ridge").fit(tr[nomo], tr.S).predict(te[nomo])
        for f, sgn in SINGLE.items():
            te[f"single_{f}"] = sgn * te[f]
        te["random"] = 0.0
        blocks.append(te)
    import pandas as pd
    pred = pd.concat(blocks, ignore_index=True)
    names = ["ridge_resid_all", "ridge_resid_nomomentum", "random"] + [f"single_{f}" for f in SINGLE]
    rng = np.random.default_rng(d.SEED)
    topics = pred.topic.unique()
    idx = {k: np.where(pred.topic.to_numpy() == k)[0] for k in topics}
    auc = lambda x, n: roc_auc_score(x.y, x[n]) if x[n].std() > 0 else 0.5  # noqa: E731
    point = {n: auc(pred, n) for n in names}
    boot = {n: [] for n in names}
    for _ in range(d.REPS):
        x = pred.iloc[np.concatenate([idx[k] for k in rng.choice(topics, len(topics))])]
        for n in names:
            boot[n].append(auc(x, n))
    ci = {n: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for n, v in boot.items()}
    per = {int(t): {n: auc(g, n) for n in names} for t, g in pred.groupby("origin")}
    gates = {"S1_ridge_resid_all_lower_gt_0.5": ci["ridge_resid_all"][0] > 0.5,
             "S2_any_single_lower_gt_0.5": any(ci[f"single_{f}"][0] > 0.5 for f in SINGLE)}
    out = {"preregistration": "research/preregistration_cs_direction_surprise_v1.md",
           "n_rows": int(len(pred)), "auroc": point, "auroc_ci95": ci, "per_origin": per,
           "gates": gates, "single_signal_tests": len(SINGLE)}
    if gates["S1_ridge_resid_all_lower_gt_0.5"]:
        tr = df[(df.origin <= 2020) & df.G.notna()].copy()
        te = df[df.origin == 2025].copy()
        tr["S"], _, _ = residualize(tr, tr.iloc[:0].assign(G=[]))
        te["surprise_score"] = d.model("ridge").fit(tr[d.FEATS], tr.S).predict(te[d.FEATS])
        te["rank_surprise"] = te.surprise_score.rank(ascending=False, method="min").astype(int)
        cols = ["topic", "name", "subfield", "P_o", "g3", "accel", "diffusion", "d_diffusion3",
                "volatility", "surprise_score", "rank_surprise"]
        csv = OUT / "prospective_surprise_2030.csv"
        te.sort_values("rank_surprise")[cols].round(8).to_csv(csv, index=False)
        out["prospective"] = {"csv": str(csv.relative_to(ROOT)),
                              "sha256": hashlib.sha256(csv.read_bytes()).hexdigest(),
                              "registered_utc": datetime.now(timezone.utc).isoformat(),
                              "evaluate_not_before": "2031-06-01"}
    (OUT / "surprise_backtest.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(json.dumps({k: out[k] for k in ("n_rows", "auroc", "auroc_ci95", "gates")} |
                     ({"prospective": out["prospective"]} if "prospective" in out else {}),
                     indent=1, default=float))


if __name__ == "__main__":
    main()
