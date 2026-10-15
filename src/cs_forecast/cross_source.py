"""Cross-source label check (amendment 1, gate G4): OpenAlex vs Semantic Scholar outcomes.

Frozen in research/preregistration_cs_breakthrough_forecast_v1_amendment1_s2.md.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROBUST_KAPPA_LOWER = 0.60
DEPENDENT_KAPPA_POINT = 0.40


def s2_cites_3y(citing_years: list, year: int, window: int = 3) -> tuple[int, int]:
    """Distinct citing papers dated y+1..y+window, and the number with a null year."""
    n_null = sum(1 for c in citing_years if c is None)
    n = sum(1 for c in citing_years if c is not None and year < int(c) <= year + window)
    return n, n_null


def top_decile_label(df: pd.DataFrame, col: str) -> pd.Series:
    thr = df.groupby("year")[col].transform(lambda s: s.quantile(0.9))
    return (df[col] >= thr).astype(int)


def cohen_kappa(a, b) -> float:
    a, b = np.asarray(a, int), np.asarray(b, int)
    po = float((a == b).mean())
    pe = float(a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean()))
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def agreement(df: pd.DataFrame, a: str, b: str, ca: str, cb: str) -> dict:
    pos_a = df[a] == 1
    return {"n": int(len(df)), "positives_a": int(pos_a.sum()), "positives_b": int(df[b].sum()),
            "kappa": cohen_kappa(df[a], df[b]),
            "raw_agreement": float((df[a] == df[b]).mean()),
            "share_a_positives_also_b": float(df.loc[pos_a, b].mean()) if pos_a.any() else None,
            "spearman_log_cites": float(spearmanr(np.log1p(df[ca]), np.log1p(df[cb])).statistic)}


def bootstrap_agreement(df: pd.DataFrame, a: str, b: str, ca: str, cb: str, reps: int = 2000,
                        seed: int = 20261014) -> dict:
    """95% intervals for kappa and Spearman, resampling frame year x topic cells."""
    rng = np.random.default_rng(seed)
    cells = df["cell"].unique()
    groups = {c: np.where(df["cell"].to_numpy() == c)[0] for c in cells}
    ka, sp = [], []
    for _ in range(reps):
        d = df.iloc[np.concatenate([groups[c] for c in rng.choice(cells, len(cells))])]
        k = cohen_kappa(d[a], d[b])
        if np.isfinite(k):
            ka.append(k)
        sp.append(spearmanr(np.log1p(d[ca]), np.log1p(d[cb])).statistic)
    ci = lambda v: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]  # noqa: E731
    return {"reps": reps, "seed": seed, "kappa_ci95": ci(ka), "spearman_ci95": ci(sp)}


def g4_verdict(kappa: float, kappa_lower: float) -> str:
    if kappa_lower >= ROBUST_KAPPA_LOWER:
        return "robust"
    if kappa < DEPENDENT_KAPPA_POINT:
        return "source_dependent"
    return "inconclusive"
