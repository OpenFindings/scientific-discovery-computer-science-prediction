#!/usr/bin/env python3
"""Score the CS-adapted Paper 3 model against frozen baselines (rolling-origin, embargo 3y).

Implements research/preregistration_cs_breakthrough_forecast_v1.md. Input is the cached
OpenAlex snapshot from scripts/fetch_openalex_frame.py; output goes to results/cs_forecast_v1/.

    python3 scripts/run_cs_forecast.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cs_forecast import evaluate as ev  # noqa: E402
from cs_forecast.features import outcome, paper_features, retrieval_features  # noqa: E402
from cs_forecast.topics import primary_subfield  # noqa: E402

DATA = ROOT / "data/cs_forecast"
OUT = ROOT / "results/cs_forecast_v1"
TARGET = "y_breakthrough"


def build_frame() -> pd.DataFrame:
    recs = [json.loads(line) for line in open(DATA / "snapshot_v1.jsonl")]
    topic_years = json.loads((DATA / "topic_years.json").read_text())
    pairs = json.loads((DATA / "topic_pairs.json").read_text())
    rows = []
    for p in recs:
        f = paper_features(p, topic_years, pairs)
        f.update(paper_id=p["paper_id"], year=p["year"], frame_topic=p["frame_topic"],
                 title=p["title"], text=f"{p['title']}. {p.get('abstract') or ''}",
                 has_abstract=bool(p.get("abstract")), cites_3y=outcome(p),
                 cs_subfield=primary_subfield(p["title"], p.get("abstract") or ""))
        rows.append(f)
    df = pd.DataFrame(rows)
    retr = retrieval_features(df["text"].tolist(), df["year"].tolist(), df["title"].tolist())
    for k in ("ev_frame_top5_sim", "nov_nn_distance", "nov_review_overlap"):
        df[k] = [r.get(k, np.nan) for r in retr]
    df["cell"] = df["year"].astype(str) + ":" + df["frame_topic"]
    thr = df.groupby("year")["cites_3y"].transform(lambda s: s.quantile(0.9))
    df[TARGET] = (df["cites_3y"] >= thr).astype(int)
    nr = df[df.txt_is_review == 0]
    thr2 = nr.groupby("year")["cites_3y"].transform(lambda s: s.quantile(0.9))
    df["y_breakthrough_no_review"] = np.nan
    df.loc[nr.index, "y_breakthrough_no_review"] = (nr["cites_3y"] >= thr2).astype(int)
    return df


def score(df, target, preds, label):
    pred = ev.rolling_origin(df, target, preds)
    names = list(preds)
    res = {n: ev.metrics(pred[target], pred[n], pred["cites_3y"]) for n in names}
    baselines = ["publication_count", "citation_trend", "research_trend",
                 "simple_statistical", "text_similarity_knn"]
    best = max((b for b in baselines if b in res), key=lambda b: res[b].get("auroc", 0))
    boot = ev.cluster_bootstrap(pred, target, names, ref=best)
    per_year = {int(t): {n: ev.metrics(g[target], g[n]).get("auroc") for n in names}
                for t, g in pred.groupby("year")}
    return pred, {"label": label, "target": target, "metrics": res,
                  "best_baseline": best, "bootstrap": boot, "per_test_year_auroc": per_year}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = build_frame()
    df.drop(columns=["text"]).to_csv(OUT / "features.csv", index=False)
    summary = {"n_papers": int(len(df)), "n_with_abstract": int(df.has_abstract.sum()),
               "positives_by_year": df.groupby("year")[TARGET].sum().astype(int).to_dict(),
               "threshold_cites_3y_by_year":
                   df.groupby("year")["cites_3y"].quantile(0.9).to_dict(),
               "cs_subfield_counts": df.cs_subfield.value_counts().to_dict()}
    preds = ev.predictors(df)

    # A2 + A3: primary rolling-origin backtest and paired deltas
    pred, primary = score(df, TARGET, preds, "primary")
    pred.to_csv(OUT / "predictions_primary.csv", index=False)
    p3 = primary["bootstrap"]["auroc_ci95"]["paper3_cs_logistic"]
    comb = primary["bootstrap"]["delta_auroc_ci95"]["combined_logistic"]
    primary["gates"] = {
        "G1_signal_paper3_auroc_lower_gt_0.5": bool(p3[0] > 0.5),
        "G2_combined_minus_best_baseline_lower_gt_0": bool(comb[0] > 0),
    }
    # A9: title-only text features
    d9 = df.copy()
    for c in [c for c in df.columns if c.startswith("txt_")]:
        d9[c] = df["title_" + c]
    _, a9 = score(d9, TARGET, {"paper3_cs_logistic": ev.predictors(d9)["paper3_cs_logistic"],
                               "citation_trend": preds["citation_trend"],
                               "text_similarity_knn": preds["text_similarity_knn"]}, "title_only")
    # A7: ablations
    abl = {}
    for g in ev.GROUPS:
        for mode, groups in (("without", [x for x in ev.GROUPS if x != g]), ("only", [g])):
            cols = ev.group_cols(df, groups)
            fn = (lambda c: lambda tr, te, t: ev._fit_predict(c, tr, te, t, "logistic"))(cols)
            pr = ev.rolling_origin(df, TARGET, {"m": fn})
            abl[f"{mode}_{g}"] = ev.metrics(pr[TARGET], pr["m"]).get("auroc")
    # A6: survey/review exclusion
    d6 = df[df.y_breakthrough_no_review.notna()].copy()
    d6["y_breakthrough_no_review"] = d6["y_breakthrough_no_review"].astype(int)
    _, a6 = score(d6, "y_breakthrough_no_review", ev.predictors(d6), "no_review")
    # A8: leave-one-frame-topic-out (pooled over topics; time order not enforced -> sensitivity)
    loto = {}
    cols = ev.group_cols(df)
    for topic in sorted(df.frame_topic.unique()):
        tr, te = df[df.frame_topic != topic], df[df.frame_topic == topic]
        if te[TARGET].nunique() == 2:
            loto[topic] = ev.metrics(te[TARGET],
                                     ev._fit_predict(cols, tr, te, TARGET, "logistic")).get("auroc")
    # A4: permutation null
    perm = ev.permutation_null(df, TARGET, preds["paper3_cs_logistic"], reps=200)
    # standardized coefficients on all matured years (descriptive, not a forecast)
    m = ev.make_model("logistic").fit(df[cols], df[TARGET])
    coefs = dict(sorted(zip(cols, m.named_steps["clf"].coef_[0].round(4).tolist()),
                        key=lambda kv: -abs(kv[1])))

    for name, obj in (("summary", summary), ("primary", primary), ("title_only", a9),
                      ("ablations", abl), ("no_review", a6), ("leave_topic_out", loto),
                      ("permutation_null", perm), ("coefficients_all_years", coefs)):
        (OUT / f"{name}.json").write_text(json.dumps(obj, indent=2, default=float) + "\n")
    print(json.dumps({"primary": {k: v.get("auroc") for k, v in primary["metrics"].items()},
                      "gates": primary["gates"], "best_baseline": primary["best_baseline"],
                      "perm_p": perm["p_value"]}, indent=2))


if __name__ == "__main__":
    main()
