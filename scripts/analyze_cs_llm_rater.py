#!/usr/bin/env python3
"""Amendment 3: LLM reference rater vs human labels and vs the citation label.

Frozen in research/preregistration_cs_breakthrough_forecast_v1_amendment3_llm_rater.md.
Run only after scripts/llm_rate_cs_papers.py has finished (or stopped at the cost cap).
Output: results/cs_forecast_v1/llm_rater.json

    python3 scripts/analyze_cs_llm_rater.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import fisher_exact, spearmanr

from analyze_cs_g3_labels import NAMES, cliffs_delta, compare

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results/cs_forecast_v1"
RAW = ROOT / "data/cs_forecast/llm_ratings_raw.jsonl"
SEED, REPS, MIN_N = 20261017, 10000, 10


def weighted_kappa(a, b, cats=(1, 2, 3)) -> float:
    a, b = np.asarray(a), np.asarray(b)
    k = len(cats)
    idx = {c: i for i, c in enumerate(cats)}
    obs = np.zeros((k, k))
    for x, y in zip(a, b):
        obs[idx[x], idx[y]] += 1
    obs /= obs.sum()
    exp = np.outer(obs.sum(1), obs.sum(0))
    w = np.array([[(i - j) ** 2 for j in range(k)] for i in range(k)]) / (k - 1) ** 2
    den = (w * exp).sum()
    return float(1 - (w * obs).sum() / den) if den > 0 else float("nan")


def agreement(pairs: list[tuple[int, int]], rng) -> dict:
    """pairs of (reference, llm) labels, both in 1..3."""
    n = len(pairs)
    if n < 2:
        return {"n": n}
    a, b = np.array([p[0] for p in pairs]), np.array([p[1] for p in pairs])
    boot = []
    for _ in range(REPS):
        i = rng.integers(0, n, n)
        boot.append(weighted_kappa(a[i], b[i]))
    boot = np.array(boot)
    boot = boot[~np.isnan(boot)]
    rho = spearmanr(a, b).statistic if len(set(a)) > 1 and len(set(b)) > 1 else float("nan")
    conf = {f"{x}": {f"{y}": int(((a == x) & (b == y)).sum()) for y in (1, 2, 3)}
            for x in (1, 2, 3)}
    return {"n": n, "weighted_kappa": weighted_kappa(a, b),
            "weighted_kappa_ci95": [float(np.percentile(boot, 2.5)),
                                    float(np.percentile(boot, 97.5))] if len(boot) else None,
            "spearman_rho": float(rho), "exact_agreement": float((a == b).mean()),
            "within_one": float((abs(a - b) <= 1).mean()),
            "mean_reference": float(a.mean()), "mean_llm": float(b.mean()),
            "confusion_reference_rows_llm_cols": conf}


def kappa_diff(p1, p2, rng) -> dict:
    if len(p1) < 2 or len(p2) < 2:
        return {"available": False}
    a1, a2 = np.array(p1), np.array(p2)
    d = []
    for _ in range(REPS):
        s1, s2 = a1[rng.integers(0, len(a1), len(a1))], a2[rng.integers(0, len(a2), len(a2))]
        d.append(weighted_kappa(s1[:, 0], s1[:, 1]) - weighted_kappa(s2[:, 0], s2[:, 1]))
    d = np.array(d)
    d = d[~np.isnan(d)]
    return {"available": True,
            "diff": weighted_kappa(a1[:, 0], a1[:, 1]) - weighted_kappa(a2[:, 0], a2[:, 1]),
            "diff_ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]}


def band(k: float) -> str:
    if k != k:
        return "undefined"
    return ("slight" if k < 0.2 else "fair" if k < 0.4 else "moderate" if k < 0.6
            else "substantial" if k < 0.8 else "near_perfect")


def ratings(log: list[dict], rater: str, pas: int) -> dict:
    return {e["id"]: e["parsed"] for e in log
            if e["rater"] == rater and e["pass"] == pas and e["status"] == "ok"}


def stratum_contrasts(r: dict, strata: dict, inv: dict, rng, subset=None) -> dict:
    by = {s: [] for s in NAMES}
    zeros = {s: 0 for s in NAMES}
    for pid, st in strata.items():
        if pid not in r or (subset is not None and r[pid]["recognized"] != subset):
            continue
        v = r[pid]["label"]
        if v == 0:
            zeros[inv[st]] += 1
        else:
            by[inv[st]].append(v)
    out = {"n_rated_1to3": {s: len(v) for s, v in by.items()}, "label_0": zeros,
           "distribution": {s: {str(k): by[s].count(k) for k in (1, 2, 3)} for s in NAMES}}
    for name, (x, y) in (("A2a_T_vs_R", ("T", "R")), ("A2c_M_vs_R", ("M", "R"))):
        out[name] = (compare(by[x], by[y], rng) if len(by[x]) >= 2 and len(by[y]) >= 2
                     else {"n_a": len(by[x]), "n_b": len(by[y]), "available": False})
    a = out["A2a_T_vs_R"]
    if len(by["T"]) < MIN_N or len(by["R"]) < MIN_N:
        out["A2a_verdict"] = "descriptive_only_n_below_10"
    else:
        lo, hi = a["cliffs_delta_ci95"]
        out["A2a_verdict"] = ("associated_with_citation_label" if lo > 0
                              else "no_more_than_small_association" if hi < 0.2
                              else "inconclusive")
    return out


def rater_block(r: dict, human: dict, strata: dict, inv: dict, rng) -> dict:
    pairs = {"all": [], "recognized": [], "unrecognized": []}
    zero_xtab = {"human0_llm_nonzero": 0, "human_nonzero_llm0": 0, "both0": 0}
    for pid, h in human.items():
        if pid not in r:
            continue
        hv, lv = h["label"], r[pid]["label"]
        if hv == 0 or lv == 0:
            zero_xtab["both0" if hv == lv else
                      "human0_llm_nonzero" if hv == 0 else "human_nonzero_llm0"] += 1
            continue
        pairs["all"].append((hv, lv))
        pairs["recognized" if r[pid]["recognized"] else "unrecognized"].append((hv, lv))
    a1 = {k: agreement(v, rng) for k, v in pairs.items()}
    for v in a1.values():
        if "weighted_kappa" in v:
            v["band"] = band(v["weighted_kappa"])
    a1["kappa_diff_recognized_minus_unrecognized"] = kappa_diff(
        pairs["recognized"], pairs["unrecognized"], rng)
    a1["zero_label_crosstab"] = zero_xtab

    rec = {s: [0, 0] for s in NAMES}  # [recognized, rated]
    for pid, st in strata.items():
        if pid in r:
            rec[inv[st]][1] += 1
            rec[inv[st]][0] += int(r[pid]["recognized"])
    (tr, tn), (rr, rn) = rec["T"], rec["R"]
    lab_rec = [r[p]["label"] for p in r if r[p]["recognized"] and r[p]["label"] > 0]
    lab_unr = [r[p]["label"] for p in r if not r[p]["recognized"] and r[p]["label"] > 0]
    a3 = {"recognized_by_stratum": {s: {"recognized": v[0], "rated": v[1],
                                        "share": v[0] / v[1] if v[1] else None}
                                    for s, v in rec.items()},
          "fisher_p_T_vs_R": float(fisher_exact([[tr, tn - tr], [rr, rn - rr]]).pvalue)
          if tn and rn else None,
          "mean_label_recognized": float(np.mean(lab_rec)) if lab_rec else None,
          "mean_label_unrecognized": float(np.mean(lab_unr)) if lab_unr else None,
          "n_recognized": len(lab_rec), "n_unrecognized": len(lab_unr)}
    a2 = {"unrecognized_primary": stratum_contrasts(r, strata, inv, rng, subset=False),
          "all": stratum_contrasts(r, strata, inv, rng),
          "recognized": stratum_contrasts(r, strata, inv, rng, subset=True)}
    return {"n_rated": len(r), "A1_human_agreement": a1, "A2_citation_label": a2,
            "A3_recognition": a3}


def between(r1: dict, r2: dict, rng) -> dict:
    common = [p for p in r1 if p in r2]
    pairs = [(r1[p]["label"], r2[p]["label"]) for p in common
             if r1[p]["label"] > 0 and r2[p]["label"] > 0]
    out = agreement(pairs, rng)
    if "weighted_kappa" in out:
        out["band"] = band(out["weighted_kappa"])
    out["n_common"] = len(common)
    out["recognition_agreement"] = (float(np.mean([r1[p]["recognized"] == r2[p]["recognized"]
                                                   for p in common])) if common else None)
    return out


def main() -> None:
    log = [json.loads(l) for l in RAW.read_text().splitlines() if l.strip()]
    human = json.loads((ROOT / "data/cs_forecast/human_labels_v1.json").read_text())["labels"]
    strata = json.loads((RES / "labeling_key.json").read_text())["strata"]
    inv = {v: k for k, v in NAMES.items()}
    rng = np.random.default_rng(SEED)
    r1, r2, r1b = ratings(log, "R1", 1), ratings(log, "R2", 1), ratings(log, "R1", 2)
    spend = {}
    for e in log:
        spend[e["model"]] = spend.get(e["model"], 0.0) + e["cost_usd"]
    status = {}
    for e in log:
        k = f'{e["rater"]}_pass{e["pass"]}'
        status.setdefault(k, {})
        status[k][e["status"]] = status[k].get(e["status"], 0) + 1
    out = {"amendment": "research/preregistration_cs_breakthrough_forecast_v1_amendment3_llm_rater.md",
           "role": "reference rater only; not independent validation; G3 verdicts unchanged",
           "calls": len(log), "call_status": status,
           "spend_usd_by_model": spend, "spend_usd_total": sum(spend.values()),
           "R1_primary": rater_block(r1, human, strata, inv, rng) if r1 else None,
           "R2_secondary": rater_block(r2, human, strata, inv, rng) if r2 else None,
           "A4_reliability": {"R1_pass1_vs_pass2": between(r1, r1b, rng) if r1b else None,
                              "R1_vs_R2": between(r1, r2, rng) if r2 else None},
           "seed": SEED, "reps": REPS}
    (RES / "llm_rater.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=1)[:6000])


if __name__ == "__main__":
    main()
