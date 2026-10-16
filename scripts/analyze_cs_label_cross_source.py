#!/usr/bin/env python3
"""Amendment 1 analyses S1-S3 and gate G4 (OpenAlex vs Semantic Scholar outcome label).

Run once, after scripts/run_cs_forecast.py (amendment 1, order of operations). Reads cached S2
responses only (any uncached request raises). Outputs results/cs_forecast_v1/cross_source_s2.json
and the committed derived counts data/cs_forecast_s2/derived_counts.csv.

    python3 scripts/analyze_cs_label_cross_source.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cs_forecast import cross_source as cs  # noqa: E402
from cs_forecast import evaluate as ev  # noqa: E402


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    fc, s2 = load("run_cs_forecast"), load("fetch_s2_frame")
    s2.MAX_REQUESTS = 0  # cache only: never touch the network here
    if not (fc.OUT / "primary.json").exists():
        sys.exit("run scripts/run_cs_forecast.py first (amendment 1 order of operations)")
    manifest = json.loads((s2.OUT / "fetch_manifest.json").read_text())
    df = fc.build_frame()

    # rebuild the fetch's exact batches (all unique frame ids, in frame order) so they hit the cache
    ids, seen = [], set()
    for line in open(ROOT / "data/historical_cs_year_topic_frame.jsonl"):
        a = json.loads(line)["arxiv_id"]
        if a not in seen:
            seen.add(a)
            ids.append(a)
    found = {}
    for i in range(0, len(ids), 500):
        chunk = ids[i:i + 500]
        r = s2.call(f"{s2.API}/paper/batch?fields=paperId,externalIds,title,year",
                    {"ids": [f"arXiv:{a}" for a in chunk]})
        found.update({a: p["paperId"] for a, p in zip(chunk, r["data"] or []) if p})
    rows, excluded = [], {"not_in_s2": 0, "citations_incomplete": 0}
    for pid, year in zip(df.paper_id, df.year):
        if pid not in found:
            excluded["not_in_s2"] += 1
            continue
        years, ok = s2.citing_years(found[pid])
        if not ok:
            excluded["citations_incomplete"] += 1
            continue
        n, n_null = cs.s2_cites_3y(years, int(year))
        rows.append({"paper_id": pid, "s2_paper_id": found[pid], "cites_3y_s2": n,
                     "citing_null_year": n_null})
    counts = pd.DataFrame(rows)
    counts.to_csv(s2.OUT / "derived_counts.csv", index=False)

    joint = df.merge(counts, on="paper_id")
    joint["y_breakthrough_s2"] = cs.top_decile_label(joint, "cites_3y_s2")
    coverage = len(joint) / len(df)
    s1 = cs.agreement(joint, fc.TARGET, "y_breakthrough_s2", "cites_3y", "cites_3y_s2")
    boot = cs.bootstrap_agreement(joint, fc.TARGET, "y_breakthrough_s2", "cites_3y",
                                  "cites_3y_s2")
    _, s3 = fc.score(joint, "y_breakthrough_s2", ev.predictors(joint), "s2_label")
    p3 = s3["bootstrap"]["auroc_ci95"]["paper3_cs_logistic"]
    comb = s3["bootstrap"]["delta_auroc_ci95"]["combined_logistic"]
    s3["gates"] = {"G1_signal_paper3_auroc_lower_gt_0.5": bool(p3[0] > 0.5),
                   "G2_combined_minus_best_baseline_lower_gt_0": bool(comb[0] > 0)}
    primary_gates = json.loads((fc.OUT / "primary.json").read_text())["gates"]
    out = {
        "amendment": "research/preregistration_cs_breakthrough_forecast_v1_amendment1_s2.md",
        "s2_fetch": {k: manifest[k] for k in ("started_utc", "finished_utc", "s2_matched",
                                              "citations_complete", "requests", "errors")},
        "n_openalex_frame": int(len(df)), "n_joint": int(len(joint)),
        "coverage_of_openalex_matched": coverage, "coverage_below_90pct": coverage < 0.9,
        "excluded": excluded, "citing_null_year_total": int(counts.citing_null_year.sum()),
        "S1_S2_agreement": s1, "S1_S2_bootstrap": boot,
        "G4": cs.g4_verdict(s1["kappa"], boot["kappa_ci95"][0]),
        "S3_forecast_under_s2_label": s3, "primary_gates_openalex_label": primary_gates,
        "gates_source_sensitive": s3["gates"] != primary_gates,
    }
    (fc.OUT / "cross_source_s2.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(json.dumps({k: out[k] for k in ("n_joint", "coverage_of_openalex_matched", "G4",
                                          "gates_source_sensitive")}, indent=2))
    print(json.dumps({"kappa": s1["kappa"], **boot, "S3_gates": s3["gates"]}, indent=2))


if __name__ == "__main__":
    main()
