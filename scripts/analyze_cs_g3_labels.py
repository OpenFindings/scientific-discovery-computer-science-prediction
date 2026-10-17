#!/usr/bin/env python3
"""G3: blinded human labels vs the citation label (amendment 2).

Frozen in research/preregistration_cs_breakthrough_forecast_v1_amendment2_g3.md.
Output: results/cs_forecast_v1/g3_human_labels.json

    python3 scripts/analyze_cs_g3_labels.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import fisher_exact, mannwhitneyu

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results/cs_forecast_v1"
SEED, REPS = 20261017, 10000
NAMES = {"T": "citation_top_decile", "R": "random_citation_negative",
         "M": "model_high_citation_negative"}


def cliffs_delta(a, b) -> float:
    a, b = np.asarray(a)[:, None], np.asarray(b)[None, :]
    return float((a > b).mean() - (a < b).mean())


def compare(a, b, rng) -> dict:
    boot = [cliffs_delta(rng.choice(a, len(a)), rng.choice(b, len(b))) for _ in range(REPS)]
    out = {"n_a": len(a), "n_b": len(b), "mean_a": float(np.mean(a)), "mean_b": float(np.mean(b)),
           "cliffs_delta": cliffs_delta(a, b),
           "cliffs_delta_ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
           "mannwhitney_p": float(mannwhitneyu(a, b, alternative="two-sided").pvalue)}
    for k, thr in (("ge2", 2), ("eq3", 3)):
        xa, xb = int((np.asarray(a) >= thr).sum()), int((np.asarray(b) >= thr).sum())
        out[f"share_{k}_a"], out[f"share_{k}_b"] = xa / len(a), xb / len(b)
        out[f"fisher_p_{k}"] = float(fisher_exact([[xa, len(a) - xa], [xb, len(b) - xb]]).pvalue)
    return out


def main() -> None:
    labels = json.loads((ROOT / "data/cs_forecast/human_labels_v1.json").read_text())["labels"]
    strata = json.loads((RES / "labeling_key.json").read_text())["strata"]
    inv = {v: k for k, v in NAMES.items()}
    by, counts = {s: [] for s in NAMES}, {s: {"in_sample": 0, "labeled": 0, "cant_judge": 0}
                                          for s in NAMES}
    for pid, st in strata.items():
        s = inv[st]
        counts[s]["in_sample"] += 1
        if pid in labels:
            counts[s]["labeled"] += 1
            v = labels[pid]["label"]
            if v == 0:
                counts[s]["cant_judge"] += 1
            else:
                by[s].append(v)
    unknown = sorted(set(labels) - set(strata))
    rng = np.random.default_rng(SEED)
    g3a, g3c = compare(by["T"], by["R"], rng), compare(by["M"], by["R"], rng)
    lo, hi = g3a["cliffs_delta_ci95"]
    verdict_a = ("citation_label_tracks_human_value" if lo > 0
                 else "H3_favoured" if hi < 0.2 else "inconclusive")
    verdict_c = ("structure_captures_value_citations_miss" if g3c["cliffs_delta_ci95"][0] > 0
                 else "no_evidence")
    dist = {s: {str(k): int(sum(1 for v in by[s] if v == k)) for k in (1, 2, 3)} for s in NAMES}
    out = {"amendment": "research/preregistration_cs_breakthrough_forecast_v1_amendment2_g3.md",
           "labels_total": len(labels), "labels_not_in_key": unknown, "counts": counts,
           "label_distribution": dist, "G3a_T_vs_R": g3a, "G3a_verdict": verdict_a,
           "G3c_M_vs_R": g3c, "G3c_verdict": verdict_c, "seed": SEED, "reps": REPS}
    (RES / "g3_human_labels.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
