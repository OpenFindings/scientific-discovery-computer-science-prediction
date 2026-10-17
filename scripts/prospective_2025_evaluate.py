#!/usr/bin/env python3
"""Amendment 8 evaluation of the registered 2025 forecasts. Refuses to run before 2029-04-01.

    python3 scripts/prospective_2025_evaluate.py
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cs_forecast import evaluate as ev  # noqa: E402

OUT = ROOT / "results/prospective_2025"
NOT_BEFORE = date(2029, 4, 1)
YEAR_END_BASELINES = ["citation_trend", "publication_count", "research_trend",
                      "simple_statistical", "text_similarity_knn"]
POSTING_BASELINES = ["posting_publication_count", "posting_research_trend",
                     "posting_simple_statistical", "text_similarity_knn"]


def main() -> None:
    if date.today() < NOT_BEFORE:
        sys.exit(f"amendment 8: evaluation not allowed before {NOT_BEFORE}")
    man = json.loads((OUT / "manifest.json").read_text())
    csv = OUT / "predictions.csv"
    if hashlib.sha256(csv.read_bytes()).hexdigest() != man["predictions_sha256"]:
        sys.exit("predictions.csv does not match the registered hash")
    pred = pd.read_csv(csv, dtype={"paper_id": str})
    spec = importlib.util.spec_from_file_location("oa", ROOT / "scripts/fetch_openalex_frame.py")
    oa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oa)
    oa.CACHE = ROOT / "data/prospective_2025/outcome_cache"
    snap = {json.loads(l)["paper_id"]: json.loads(l)
            for l in open(ROOT / "data/prospective_2025/snapshot.jsonl")}
    cites = []
    for pid in pred.paper_id:
        s = snap[pid]
        ids = {s["feature_work"]}
        q = re.sub(r"[,:|!?()\[\]\"']", " ", s["title"])
        r = oa.get({"filter": f"title.search:{q},publication_year:2025-2028", "per_page": 25,
                    "select": "id,display_name"})
        want = oa.norm_title(s["title"])
        ids |= {oa.short(w["id"]) for w in r.get("data", {}).get("results", [])
                if oa.norm_title(w["display_name"]) == want}
        r = oa.get({"filter": "cites:" + "|".join(sorted(ids)) + ",publication_year:2026-2028",
                    "per_page": 1, "select": "id"})
        cites.append(r["data"]["meta"]["count"])
    pred["cites_3y"] = cites
    pred["y"] = (pred.cites_3y >= pred.cites_3y.quantile(0.9)).astype(int)
    pred["cell"] = pred.frame_topic
    names = [c for c in pred.columns if c not in ("paper_id", "frame_topic", "cs_subfield",
                                                  "cites_3y", "y", "cell")]
    metrics = {n: ev.metrics(pred.y, pred[n], pred.cites_3y) for n in names}
    best_ye = max(YEAR_END_BASELINES, key=lambda b: metrics[b].get("auroc", 0))
    best_po = max(POSTING_BASELINES, key=lambda b: metrics[b].get("auroc", 0))
    b1 = ev.cluster_bootstrap(pred, "y", names, ref=best_ye)
    b2 = ev.cluster_bootstrap(pred, "y", names, ref=best_po)
    gates = {"P1": b1["auroc_ci95"]["paper3_cs_logistic"][0] > 0.5,
             "P2": b1["delta_auroc_ci95"]["combined_logistic"][0] > 0,
             "P3": b2["delta_auroc_ci95"]["posting_combined_logistic"][0] > 0}
    (OUT / "evaluation.json").write_text(json.dumps(
        {"metrics": metrics, "best_year_end_baseline": best_ye, "best_posting_baseline": best_po,
         "bootstrap_year_end": b1, "bootstrap_posting": b2, "gates": gates}, indent=2,
        default=float) + "\n")
    print(json.dumps(gates))


if __name__ == "__main__":
    main()
