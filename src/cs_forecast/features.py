"""Cutoff-time feature groups A-F for CS papers (CS adaptation of Paper 3 features.py).

A text (txt_), B evidence context (ev_), C novelty (nov_), D falsifiability (fal_),
E tractability (tra_), F environment (env_). Baseline-only inputs use the base_ prefix and are
never part of the Paper 3 model. Every feature uses only information dated on or before
31 Dec of the paper's publication year.
"""

from __future__ import annotations

import math
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .tractability import tractability_features

# ---------------------------------------------------------------- group A

_CAUSAL = re.compile(r"\b(caus\w+|due to|why|mechanis\w+|explain\w*|lead(?:s|ing)? to|root cause)\b", re.I)
_COMPARISON = re.compile(r"\b(than|compar\w+|versus|vs\.?|outperform\w*|baseline\w*|state[- ]of[- ]the[- ]art)\b", re.I)
_MECHANISM = re.compile(r"\b(mechanis\w+|architecture|framework|pipeline|algorithm)\b", re.I)
_MEASURABLE = re.compile(
    r"\b(accuracy|precision|recall|F1|latency|throughput|speed-?up|error rate|runtime|"
    r"memory|energy|bandwidth|BLEU|AUC|complexity|overhead|coverage|scalab\w+|O\()", re.I)
_ALTERNATIVES = re.compile(r"\bwhether\b.{3,80}\bor\b|\bor (?:is|are|does|do|can|instead|rather)\b|"
                           r"\btrade-?offs?\b", re.I)
_FALSIFICATION = re.compile(r"\b(hypothes\w+|rule[sd]? out|distinguish\w*|refute\w*|"
                            r"counterexample\w*|ablation\w*|significan\w+|confound\w*)\b", re.I)
_QUESTION = re.compile(r"\?|\b(we ask|we investigate whether|open (problem|question)|remains? unclear)\b", re.I)
_CLAIM_FIRST = re.compile(r"\b(first|novel|new paradigm|unprecedented|breakthrough)\b", re.I)
_ENTITY = re.compile(r"\b[A-Z][A-Za-z]*[A-Z][A-Za-z0-9-]*\b")  # BERT, ResNet, GPT-2
_NUMBER = re.compile(r"\b\d+(?:\.\d+)?%?")
_REVIEWISH = re.compile(r"\b(survey|review|tutorial|overview|state of the art in|perspective|"
                        r"challenges and (opportunities|directions)|a primer)\b", re.I)


def is_reviewish(title: str) -> bool:
    return bool(_REVIEWISH.search(title or ""))


def text_features(text: str) -> dict:
    n_numbers = len(_NUMBER.findall(text))
    f = {
        "txt_n_words": len(text.split()),
        "txt_n_entities": len(set(_ENTITY.findall(text))),
        "txt_n_numbers": n_numbers,
        "txt_has_causal": int(bool(_CAUSAL.search(text))),
        "txt_has_comparison": int(bool(_COMPARISON.search(text))),
        "txt_has_mechanism": int(bool(_MECHANISM.search(text))),
        "txt_has_measurable": int(bool(_MEASURABLE.search(text))),
        "txt_has_alternatives": int(bool(_ALTERNATIVES.search(text))),
        "txt_has_falsification": int(bool(_FALSIFICATION.search(text))),
        "txt_poses_question": int(bool(_QUESTION.search(text))),
        "txt_claims_first": int(bool(_CLAIM_FIRST.search(text))),
        "txt_is_review": int(is_reviewish(text[:200])),
    }
    f["txt_specificity"] = (min(f["txt_n_entities"], 3) + f["txt_has_measurable"]
                            + f["txt_has_falsification"] + min(n_numbers, 2))
    return f


def falsifiability_features(text: str) -> dict:
    return {
        "fal_outcome_variable": int(bool(_MEASURABLE.search(text))),
        "fal_competing_rule": int(bool(_ALTERNATIVES.search(text))),
        "fal_quant_threshold": int(bool(_NUMBER.search(text))),
        "fal_test_wording": int(bool(_FALSIFICATION.search(text))),
    }


# ---------------------------------------------------------------- group B (references)


def reference_features(refs: list[dict], year: int) -> dict:
    """refs: [{year, topic, field, title}] already restricted to publication year <= cutoff."""
    ages = [year - r["year"] for r in refs if r.get("year") is not None]
    topics = [r.get("topic") for r in refs if r.get("topic")]
    fields = {r.get("field") for r in refs if r.get("field")}
    ent = 0.0
    if topics:
        _, counts = np.unique(topics, return_counts=True)
        p = counts / counts.sum()
        ent = float(-(p * np.log2(p)).sum())
    return {
        "ev_n_refs": len(refs),
        "ev_ref_age_mean": float(np.mean(ages)) if ages else np.nan,
        "ev_ref_age_std": float(np.std(ages)) if ages else np.nan,
        "ev_ref_recency_share": float(np.mean([a <= 2 for a in ages])) if ages else np.nan,
        "ev_ref_old_share": float(np.mean([a >= 10 for a in ages])) if ages else np.nan,
        "ev_ref_topic_entropy": ent,
        "ev_ref_review_share": (float(np.mean([is_reviewish(r.get("title", "")) for r in refs]))
                                if refs else np.nan),
        "nov_ref_field_breadth": len(fields),
    }


# ------------------------------------------------- groups B/C (earlier-year frame retrieval)


def retrieval_features(texts: list[str], years: list[int], titles: list[str]) -> list[dict]:
    """Similarity of each paper to frame papers from strictly earlier years.

    The TF-IDF vocabulary for cutoff year y is fitted only on papers with year < y.
    """
    years_arr = np.asarray(years)
    out: list[dict] = [{} for _ in texts]
    for y in sorted(set(years)):
        past = np.where(years_arr < y)[0]
        cur = np.where(years_arr == y)[0]
        if len(past) < 5:
            for i in cur:
                out[i] = {"ev_frame_top5_sim": np.nan, "nov_nn_distance": np.nan,
                          "nov_review_overlap": np.nan}
            continue
        vec = TfidfVectorizer(stop_words="english", sublinear_tf=True, min_df=1)
        P = vec.fit_transform([texts[i] for i in past])
        C = vec.transform([texts[i] for i in cur])
        S = cosine_similarity(C, P)
        review_cols = [j for j, i in enumerate(past) if is_reviewish(titles[i])]
        for row, i in enumerate(cur):
            s = np.sort(S[row])[::-1]
            out[i] = {
                "ev_frame_top5_sim": float(s[:5].mean()),
                "nov_nn_distance": float(1.0 - s[0]),
                "nov_review_overlap": float(S[row, review_cols].max()) if review_cols else 0.0,
            }
    return out


# ---------------------------------------------------------------- assemble


def paper_features(p: dict, topic_years: dict, pair_counts: dict) -> dict:
    """p: one snapshot record (see scripts/fetch_openalex_frame.py)."""
    y = p["year"]
    text = f"{p['title']}. {p.get('abstract') or ''}"
    f: dict = {}
    f.update(text_features(text))
    f.update({f"title_{k}": v for k, v in text_features(p["title"]).items()})
    f.update(falsifiability_features(text))
    f.update(tractability_features(text, y))
    refs = [r for r in p.get("refs", []) if r.get("year") is not None and r["year"] <= y]
    f.update(reference_features(refs, y))
    pairs = p.get("topic_pairs", [])
    prior = [pair_counts.get(f"{a}|{b}|{y}") for a, b in pairs]
    prior = [c for c in prior if c is not None]
    f["nov_topic_pair_prior_log"] = math.log1p(min(prior)) if prior else np.nan
    f["nov_new_topic_pair"] = int(bool(prior) and min(prior) == 0)
    counts = topic_years.get(p.get("primary_topic") or "", {})
    vol, vol2 = counts.get(str(y), 0), counts.get(str(y - 2), 0)
    f["env_topic_volume_log"] = math.log1p(vol)
    f["env_topic_growth"] = math.log((vol + 1) / (vol2 + 1))
    # baseline-only inputs (never in the Paper 3 model)
    cby = p.get("cites_by_year", {})
    f["base_cites_year0_log"] = math.log1p(cby.get(str(y), 0))
    f["base_months_to_cutoff"] = 12 - int(p["published"][5:7]) + 1
    f["base_n_authors"] = p.get("n_authors", np.nan)
    # an authorship without an OpenAlex author id ("null" key) has no known count: missing, not 0
    apc = [c for a, c in p.get("author_prior_works", {}).items()
           if c is not None and a not in (None, "null")]
    f["base_author_prior_max_log"] = math.log1p(max(apc)) if apc else np.nan
    f["base_author_prior_mean_log"] = math.log1p(float(np.mean(apc))) if apc else np.nan
    return f


def outcome(p: dict, window: int = 3) -> int:
    cby = p.get("cites_by_year", {})
    return int(sum(cby.get(str(p["year"] + k), 0) for k in range(1, window + 1)))
