"""Rolling-origin evaluation, baselines and cluster-bootstrap uncertainty.

Frozen in research/preregistration_cs_breakthrough_forecast_v1.md. For test year t the model
trains only on papers with year <= t-3, whose 3-year outcome windows have closed by 31 Dec t.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

GROUPS = {"text": "txt_", "evidence": "ev_", "novelty": "nov_", "falsifiability": "fal_",
          "tractability": "tra_", "environment": "env_"}
TEST_YEARS = tuple(range(2016, 2023))
EMBARGO = 3

BASELINE_INPUTS = {
    "publication_count": ["env_topic_volume_log", "base_author_prior_max_log",
                          "base_author_prior_mean_log"],
    "citation_trend": ["base_cites_year0_log", "base_months_to_cutoff", "env_topic_growth"],
    "research_trend": ["env_topic_growth"],
    "simple_statistical": ["ev_n_refs", "txt_n_words", "base_n_authors"],
}


def group_cols(df: pd.DataFrame, groups=None) -> list[str]:
    pref = tuple(GROUPS[g] for g in (groups or GROUPS))
    return [c for c in df.columns if c.startswith(pref)]


def make_model(kind: str = "logistic"):
    if kind == "logistic":
        clf = LogisticRegression(max_iter=5000, C=1.0)
        return Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler()),
                         ("clf", clf)])
    if kind == "gbm":
        return Pipeline([("imp", SimpleImputer(strategy="median")),
                         ("clf", GradientBoostingClassifier(n_estimators=300, max_depth=3,
                                                            learning_rate=0.05, random_state=7))])
    raise ValueError(kind)


def _fit_predict(cols, tr, te, target, kind):
    cols = [c for c in cols if tr[c].notna().any()]
    if tr[target].nunique() < 2 or not cols:
        return np.full(len(te), tr[target].mean())
    m = make_model(kind).fit(tr[cols], tr[target])
    return m.predict_proba(te[cols])[:, 1]


def _knn_text(tr, te, target, k=15):
    vec = TfidfVectorizer(stop_words="english", sublinear_tf=True)
    A = vec.fit_transform(tr["text"])
    S = cosine_similarity(vec.transform(te["text"]), A)
    yv = tr[target].to_numpy(float)
    out = []
    for row in S:
        idx = np.argsort(-row)[:k]
        w = row[idx]
        out.append(float((w * yv[idx]).sum() / w.sum()) if w.sum() > 0 else yv.mean())
    return np.asarray(out)


def predictors(df: pd.DataFrame) -> dict:
    """name -> callable(tr, te, target) returning scores for te."""
    p3 = group_cols(df)
    allb = sorted({c for v in BASELINE_INPUTS.values() for c in v})
    preds = {
        "random": lambda tr, te, t: np.full(len(te), 0.5),
        "text_similarity_knn": _knn_text,
        "paper3_cs_logistic": lambda tr, te, t: _fit_predict(p3, tr, te, t, "logistic"),
        "paper3_cs_gbm": lambda tr, te, t: _fit_predict(p3, tr, te, t, "gbm"),
        "combined_logistic": lambda tr, te, t: _fit_predict(sorted(set(p3) | set(allb)), tr, te,
                                                            t, "logistic"),
    }
    for name, cols in BASELINE_INPUTS.items():
        preds[name] = (lambda c: lambda tr, te, t: _fit_predict(c, tr, te, t, "logistic"))(cols)
    return preds


def rolling_origin(df: pd.DataFrame, target: str, preds: dict) -> pd.DataFrame:
    rows = []
    for t in TEST_YEARS:
        tr, te = df[df.year <= t - EMBARGO], df[df.year == t]
        if te.empty or tr.empty:
            continue
        block = te[["paper_id", "year", "cell", target, "cites_3y"]].copy()
        for name, fn in preds.items():
            block[name] = fn(tr, te, target)
        rows.append(block)
    return pd.concat(rows, ignore_index=True)


def ece(y, p, bins=10):
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(p, edges) - 1, 0, bins - 1)
    return float(sum(abs(y[idx == b].mean() - p[idx == b].mean()) * (idx == b).mean()
                     for b in range(bins) if (idx == b).any()))


def metrics(y, p, cites=None) -> dict:
    y, p = np.asarray(y, float), np.asarray(p, float)
    out = {"n": int(len(y)), "positives": int(y.sum())}
    if len(np.unique(y)) < 2:
        return out
    k = max(1, int(round(0.1 * len(y))))
    top = np.argsort(-p, kind="stable")[:k]
    out.update(auroc=float(roc_auc_score(y, p)), auprc=float(average_precision_score(y, p)),
               brier=float(brier_score_loss(y, p)), ece=ece(y, p),
               precision_at_10pct=float(y[top].mean()))
    if cites is not None and np.std(p) > 0:
        out["spearman_log_cites"] = float(spearmanr(p, np.log1p(cites)).statistic)
    return out


def cluster_bootstrap(pred: pd.DataFrame, target: str, names: list[str], reps=2000,
                      seed=20261014, ref: str | None = None) -> dict:
    """95% intervals for AUROC (and paired differences vs ref) resampling year x topic cells."""
    rng = np.random.default_rng(seed)
    cells = pred["cell"].unique()
    groups = {c: np.where(pred["cell"].to_numpy() == c)[0] for c in cells}
    y = pred[target].to_numpy()
    draws = {n: [] for n in names}
    diffs = {n: [] for n in names if ref and n != ref}
    for _ in range(reps):
        idx = np.concatenate([groups[c] for c in rng.choice(cells, len(cells))])
        yb = y[idx]
        if len(np.unique(yb)) < 2:
            continue
        a = {n: roc_auc_score(yb, pred[n].to_numpy()[idx]) for n in names}
        for n in names:
            draws[n].append(a[n])
        for n in diffs:
            diffs[n].append(a[n] - a[ref])
    ci = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]  # noqa: E731
    out = {"auroc_ci95": {n: ci(v) for n, v in draws.items()}}
    if ref:
        out["delta_vs"] = ref
        out["delta_auroc_ci95"] = {n: ci(v) for n, v in diffs.items()}
        out["delta_auroc_mean"] = {n: float(np.mean(v)) for n, v in diffs.items()}
    return out


def permutation_null(df: pd.DataFrame, target: str, fn, reps=200, seed=7) -> dict:
    """Shuffle labels within publication year; recompute pooled rolling-origin AUROC."""
    rng = np.random.default_rng(seed)
    obs = rolling_origin(df, target, {"m": fn})
    obs_auc = roc_auc_score(obs[target], obs["m"])
    null = []
    for _ in range(reps):
        d = df.copy()
        d[target] = d.groupby("year")[target].transform(lambda s: rng.permutation(s.to_numpy()))
        r = rolling_origin(d, target, {"m": fn})
        null.append(roc_auc_score(r[target], r["m"]))
    null = np.asarray(null)
    return {"observed_auroc": float(obs_auc), "null_mean": float(null.mean()),
            "null_p95": float(np.percentile(null, 95)), "reps": reps,
            "p_value": float((1 + (null >= obs_auc).sum()) / (reps + 1))}
