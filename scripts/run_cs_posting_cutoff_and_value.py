#!/usr/bin/env python3
"""Amendment 7: posting-time-cutoff forecast (Z1/Z2) and structure score vs value markers (D1-D3).

Frozen in research/preregistration_cs_breakthrough_forecast_v1_amendment7_posting_cutoff_and_value.md.

    python3 scripts/run_cs_posting_cutoff_and_value.py
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cs_forecast import evaluate as ev  # noqa: E402

RES = ROOT / "results/cs_forecast_v1"
DATA = ROOT / "data/cs_forecast"
SEED_D, REPS_D = 20261017, 10000


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def posting_cutoff() -> dict:
    fc = load("run_cs_forecast")
    df = fc.build_frame()
    recs = {json.loads(l)["paper_id"]: json.loads(l) for l in open(DATA / "snapshot_v1.jsonl")}
    topic_years = json.loads((DATA / "topic_years.json").read_text())
    vol, gro = [], []
    for pid, y in zip(df.paper_id, df.year):
        c = topic_years.get(recs[pid].get("primary_topic") or "", {})
        v1, v3 = c.get(str(y - 1), 0), c.get(str(y - 3), 0)
        vol.append(math.log1p(v1))
        gro.append(math.log((v1 + 1) / (v3 + 1)))
    df["env_topic_volume_log"], df["env_topic_growth"] = vol, gro
    df = df.drop(columns=["base_cites_year0_log", "base_months_to_cutoff"])
    ev.BASELINE_INPUTS = {k: v for k, v in ev.BASELINE_INPUTS.items() if k != "citation_trend"}
    preds = ev.predictors(df)
    _, res = fc.score(df, fc.TARGET, preds, "posting_cutoff")
    p3 = res["bootstrap"]["auroc_ci95"]["paper3_cs_logistic"]
    comb = res["bootstrap"]["delta_auroc_ci95"]["combined_logistic"]
    res["gates"] = {"Z1_paper3_auroc_lower_gt_0.5": bool(p3[0] > 0.5),
                    "Z2_combined_minus_best_posting_baseline_lower_gt_0": bool(comb[0] > 0)}
    prim = json.loads((RES / "primary.json").read_text())
    res["descriptive_vs_year_end"] = {
        "paper3_auroc_posting": res["metrics"]["paper3_cs_logistic"]["auroc"],
        "paper3_auroc_year_end": prim["metrics"]["paper3_cs_logistic"]["auroc"],
        "citation_trend_auroc_year_end": prim["metrics"]["citation_trend"]["auroc"],
        "combined_auroc_posting": res["metrics"]["combined_logistic"]["auroc"]}
    return res


def value_prediction() -> dict:
    rows = json.loads((RES / "value_markers_v2_analysis.json").read_text())["rows"]
    pred = pd.read_csv(RES / "predictions_primary.csv", dtype={"paper_id": str})
    f = pd.read_csv(RES / "features.csv", dtype={"paper_id": str})
    m = pd.DataFrame(rows)[["paper_id", "stratum", "V"]].merge(
        pred[["paper_id", "paper3_cs_logistic", "citation_trend"]], on="paper_id")
    n_neg_pool = int((f.y_breakthrough == 0).sum()) - 100
    w = np.where(m.stratum == "random_citation_negative", n_neg_pool / 200, 1.0)
    y, a, b = m.V.to_numpy(), m.paper3_cs_logistic.to_numpy(), m.citation_trend.to_numpy()
    rng = np.random.default_rng(SEED_D)

    def stats(weights):
        d1, d2, d3 = [], [], []
        for _ in range(REPS_D):
            i = rng.integers(0, len(y), len(y))
            if 0 < y[i].sum() < len(i):
                s1 = roc_auc_score(y[i], a[i], sample_weight=weights[i])
                s2 = roc_auc_score(y[i], b[i], sample_weight=weights[i])
                d1.append(s1), d2.append(s2), d3.append(s1 - s2)
        ci = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]  # noqa: E731
        p1 = roc_auc_score(y, a, sample_weight=weights)
        p2 = roc_auc_score(y, b, sample_weight=weights)
        return {"D1_paper3_auroc": p1, "D1_ci95": ci(d1), "D2_citation_trend_auroc": p2,
                "D2_ci95": ci(d2), "D3_difference": p1 - p2, "D3_ci95": ci(d3)}

    out = {"n_scored_searched": int(len(m)), "positives": int(y.sum()),
           "by_stratum": m.groupby("stratum").V.agg(["count", "sum"]).to_dict(),
           "unweighted": stats(np.ones(len(y))), "ipw_sensitivity": stats(w)}
    u = out["unweighted"]
    out["gates"] = {"D1_lower_gt_0.5": bool(u["D1_ci95"][0] > 0.5),
                    "D3_lower_gt_0": bool(u["D3_ci95"][0] > 0)}
    return out


def main() -> None:
    out = {"amendment": "research/preregistration_cs_breakthrough_forecast_v1_amendment7_posting_cutoff_and_value.md",
           "Z_posting_cutoff": posting_cutoff(), "D_value_prediction": value_prediction()}
    (RES / "posting_cutoff_and_value.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    z, d = out["Z_posting_cutoff"], out["D_value_prediction"]
    print(json.dumps({"Z_gates": z["gates"], "Z_best_baseline": z["best_baseline"],
                      "Z_auroc": {k: round(v["auroc"], 3) for k, v in z["metrics"].items()
                                  if "auroc" in v},
                      "Z_paper3_ci": z["bootstrap"]["auroc_ci95"]["paper3_cs_logistic"],
                      "Z_combined_delta_ci": z["bootstrap"]["delta_auroc_ci95"]["combined_logistic"],
                      "Z_vs_year_end": z["descriptive_vs_year_end"],
                      "D": {k: d[k] for k in ("n_scored_searched", "positives", "gates")},
                      "D_unweighted": d["unweighted"], "D_ipw": d["ipw_sensitivity"]},
                     indent=1, default=float))


if __name__ == "__main__":
    main()
