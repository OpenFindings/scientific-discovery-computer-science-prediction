#!/usr/bin/env python3
"""LLM reference rater for the 120 G3 labeling papers (amendment 3).

Frozen in research/preregistration_cs_breakthrough_forecast_v1_amendment3_llm_rater.md.
The model sees only title, year and abstract, exactly as on the blinded labeling page; it never
sees arXiv ids, citation counts or strata. It also reports whether it recognises the paper.

    python3 scripts/run_cs_llm_rater.py rate      # paid: OpenAI API, hard cap $5
    python3 scripts/run_cs_llm_rater.py analyze   # offline, plus free OpenAlex author lookup

Outputs in results/cs_forecast_v1/: llm_rater_raw.jsonl (append-only raw responses),
llm_rater_labels.json, llm_rater_analysis.json.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

import numpy as np
import requests
from scipy.stats import fisher_exact, mannwhitneyu, spearmanr

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results/cs_forecast_v1"
RAW = RES / "llm_rater_raw.jsonl"
MODEL = "gpt-4.1-2025-04-14"
TEMPERATURE = 0
MAX_TOKENS = 300
API_SEED = 20261017
RUNS = 3  # run 1 is primary; runs 2-3 measure test-retest stability
# OpenAI list price for gpt-4.1 (USD per token), times a 1.25 safety margin for the cap.
PRICE_IN, PRICE_OUT, MARGIN = 2.00e-6, 8.00e-6, 1.25
BUDGET_USD = 5.00
SEED, REPS = 20261017, 10000
NAMES = {"T": "citation_top_decile", "R": "random_citation_negative",
         "M": "model_high_citation_negative"}

SYSTEM = """You are an expert computer-science reviewer helping assess the contribution of \
research papers. Judge each paper's contribution as it would be seen about 3 years after its \
publication year, using this rubric:

3 - Breakthrough: opened a new direction, or became a widely adopted method, benchmark, system \
or result within ~3 years.
2 - Significant: a solid contribution that others clearly built on, but not field-changing.
1 - Incremental: a modest or narrow contribution with little visible uptake.
0 - Can't judge: outside your expertise, or not enough information.

You will see only the title, publication year and abstract. Do not try to recall or estimate \
citation counts; judge the contribution itself. Separately, say honestly whether you recognise \
this specific paper (that is, you remember it existing, not merely its topic). If you recognise \
it, give the first author's surname; otherwise give null. Do not guess an author if you do not \
recognise the paper."""

USER_TEMPLATE = "Publication year: {year}\nTitle: {title}\n\nAbstract:\n{abstract}"

SCHEMA = {
    "name": "paper_rating",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "rationale": {"type": "string",
                          "description": "At most 50 words explaining the rating."},
            "label": {"type": "integer", "enum": [0, 1, 2, 3]},
            "recognized": {"type": "boolean"},
            "first_author_surname": {"type": ["string", "null"]},
        },
        "required": ["rationale", "label", "recognized", "first_author_surname"],
    },
}


def load_items() -> list[dict]:
    html = (ROOT / "labeling/cs_breakthrough_labeling.html").read_text()
    m = re.search(r"const ITEMS=(\[.*?\]);const KEY", html, re.S)
    return json.loads(m.group(1))


def raw_records() -> list[dict]:
    if not RAW.exists():
        return []
    return [json.loads(l) for l in RAW.read_text().splitlines() if l.strip()]


def cost(usage: dict) -> float:
    return usage.get("prompt_tokens", 0) * PRICE_IN + usage.get("completion_tokens", 0) * PRICE_OUT


def rate() -> None:
    key = os.environ["OPENAI_API_KEY"]
    items = load_items()
    done = {(r["run"], r["paper_id"]) for r in raw_records() if r.get("parsed")}
    spent = sum(cost(r.get("usage", {})) for r in raw_records()) * MARGIN
    sess = requests.Session()
    for run in range(1, RUNS + 1):
        for it in items:
            if (run, it["id"]) in done:
                continue
            user = USER_TEMPLATE.format(year=it["year"], title=it["title"], abstract=it["abstract"])
            worst = ((len(SYSTEM) + len(user)) / 3 * PRICE_IN + MAX_TOKENS * PRICE_OUT) * MARGIN
            if spent + worst > BUDGET_USD:
                print(f"BUDGET STOP: spent ${spent:.4f} (with margin); next call could exceed "
                      f"${BUDGET_USD}")
                sys.exit(2)
            body = {"model": MODEL, "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS,
                    "seed": API_SEED, "response_format": {"type": "json_schema",
                                                          "json_schema": SCHEMA},
                    "messages": [{"role": "system", "content": SYSTEM},
                                 {"role": "user", "content": user}]}
            r, err = None, ""
            for attempt in range(3):
                try:
                    r = sess.post("https://api.openai.com/v1/chat/completions", json=body,
                                  headers={"Authorization": f"Bearer {key}"}, timeout=90)
                except requests.RequestException as e:
                    err = repr(e)
                    time.sleep(2 ** (attempt + 1))
                    continue
                if r.status_code == 200:
                    break
                err = f"HTTP {r.status_code}: {r.text[:300]}"
                if r.status_code in (429, 500, 502, 503):
                    time.sleep(2 ** (attempt + 2))
                    continue
                break
            rec = {"run": run, "paper_id": it["id"], "model": MODEL,
                   "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            if r is not None and r.status_code == 200:
                d = r.json()
                rec["usage"] = d.get("usage", {})
                rec["system_fingerprint"] = d.get("system_fingerprint")
                rec["model_returned"] = d.get("model")
                content = d["choices"][0]["message"].get("content")
                rec["content"] = content
                try:
                    rec["parsed"] = json.loads(content)
                except (TypeError, json.JSONDecodeError):
                    rec["error"] = "unparseable content"
            else:
                rec["error"] = err
            spent += cost(rec.get("usage", {})) * MARGIN
            with RAW.open("a") as f:
                f.write(json.dumps(rec) + "\n")
            print(f"run {run} {it['id']}: {rec.get('parsed', {}).get('label', rec.get('error'))} "
                  f"(spent ${spent:.4f})")
    print(f"done; spent ${spent:.4f} with margin, ${spent / MARGIN:.4f} at list price")


# ---------------------------------------------------------------- analysis

def cliffs_delta(a, b) -> float:
    a, b = np.asarray(a)[:, None], np.asarray(b)[None, :]
    return float((a > b).mean() - (a < b).mean())


def compare(a, b, rng) -> dict:
    if len(a) == 0 or len(b) == 0:
        return {"n_a": len(a), "n_b": len(b), "note": "empty group"}
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


def qw_kappa(x, y, cats=(1, 2, 3)) -> float:
    k = len(cats)
    idx = {c: i for i, c in enumerate(cats)}
    o = np.zeros((k, k))
    for a, b in zip(x, y):
        o[idx[a], idx[b]] += 1
    o /= o.sum()
    e = np.outer(o.sum(1), o.sum(0))
    w = np.array([[(i - j) ** 2 for j in range(k)] for i in range(k)]) / (k - 1) ** 2
    den = (w * e).sum()
    return float(1 - (w * o).sum() / den) if den > 0 else float("nan")


def agreement(x, y, rng) -> dict:
    x, y = np.asarray(x), np.asarray(y)
    n = len(x)
    if n < 3:
        return {"n": n, "note": "too few pairs"}
    boot_k, boot_r = [], []
    for _ in range(REPS):
        i = rng.integers(0, n, n)
        boot_k.append(qw_kappa(x[i], y[i]))
        boot_r.append(spearmanr(x[i], y[i]).statistic)
    ci = lambda v: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]
    return {"n": n, "quadratic_weighted_kappa": qw_kappa(x, y), "kappa_ci95": ci(boot_k),
            "spearman": float(spearmanr(x, y).statistic), "spearman_ci95": ci(boot_r),
            "exact_agreement": float((x == y).mean()),
            "within_one": float((np.abs(x - y) <= 1).mean()),
            "mean_llm_minus_human": float((x - y).mean())}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z]", "", s)


def first_authors(work_ids: dict[str, str]) -> dict[str, list[str]]:
    """Free OpenAlex lookup, used only after rating, to verify recognition claims."""
    out = {}
    for pid, wid in work_ids.items():
        r = requests.get(f"https://api.openalex.org/works/{wid}",
                         params={"select": "authorships", "mailto": "research@openfindings.org"},
                         timeout=60)
        r.raise_for_status()
        auths = r.json().get("authorships", [])
        out[pid] = [a["author"]["display_name"] for a in auths]
        time.sleep(0.15)
    return out


def analyze() -> None:
    items = load_items()
    strata = json.loads((RES / "labeling_key.json").read_text())["strata"]
    inv = {v: k for k, v in NAMES.items()}
    human = {k: v["label"] for k, v in json.loads(
        (ROOT / "data/cs_forecast/human_labels_v1.json").read_text())["labels"].items()}
    recs = [r for r in raw_records() if r.get("parsed")]
    by_run = {run: {r["paper_id"]: r["parsed"] for r in recs if r["run"] == run}
              for run in range(1, RUNS + 1)}
    prim = by_run[1]
    missing = sorted({it["id"] for it in items} - set(prim))
    usage = [r.get("usage", {}) for r in raw_records()]
    spend = sum(cost(u) for u in usage)

    # verified recognition: claimed first-author surname matches an OpenAlex author surname
    snap = {json.loads(l)["paper_id"]: json.loads(l)
            for l in open(ROOT / "data/cs_forecast/snapshot_v1.jsonl")}
    authors_path = RES / "llm_rater_openalex_authors.json"
    if authors_path.exists():
        authors = json.loads(authors_path.read_text())
    else:
        authors = first_authors({pid: snap[pid]["feature_work"] for pid in prim})
        authors_path.write_text(json.dumps(authors, indent=1) + "\n")

    def verified(pid) -> bool:
        p = prim[pid]
        guess = norm(((p.get("first_author_surname") or "").split() or [""])[-1])
        if not p["recognized"] or not guess:
            return False
        names = authors.get(pid, [])
        return bool(names) and norm(names[0].split()[-1]) == guess

    rows = []
    for it in items:
        pid = it["id"]
        if pid not in prim:
            continue
        p = prim[pid]
        rows.append({"paper_id": pid, "year": it["year"], "stratum": inv[strata[pid]],
                     "llm_label": p["label"], "recognized": bool(p["recognized"]),
                     "first_author_surname": p.get("first_author_surname"),
                     "recognition_verified": verified(pid),
                     "openalex_first_author": (authors.get(pid) or [None])[0],
                     "human_label": human.get(pid),
                     "llm_label_runs": [by_run[r].get(pid, {}).get("label") for r in by_run],
                     "rationale": p["rationale"]})
    (RES / "llm_rater_labels.json").write_text(json.dumps(
        {"model": MODEL, "temperature": TEMPERATURE, "rows": rows}, indent=1) + "\n")

    rng = np.random.default_rng(SEED)

    def subset(pred):
        return [r for r in rows if pred(r)]

    def agree(rs):
        pairs = [(r["llm_label"], r["human_label"]) for r in rs
                 if r["human_label"] in (1, 2, 3) and r["llm_label"] in (1, 2, 3)]
        return agreement([a for a, _ in pairs], [b for _, b in pairs], rng)

    def strata_tests(rs, label="llm_label"):
        g = {s: [r[label] for r in rs if r["stratum"] == s and r[label] in (1, 2, 3)]
             for s in NAMES}
        return {"T_vs_R": compare(g["T"], g["R"], rng), "M_vs_R": compare(g["M"], g["R"], rng)}

    rec = lambda r: r["recognized"]
    unrec = lambda r: not r["recognized"]
    both = lambda r: r["human_label"] is not None

    crosstab = {f"llm{a}_human{b}": sum(1 for r in rows if r["llm_label"] == a
                                        and r["human_label"] == b)
                for a in range(4) for b in range(4)}
    recog = {}
    for s in NAMES:
        rs = [r for r in rows if r["stratum"] == s]
        recog[s] = {"n": len(rs), "self_reported": sum(r["recognized"] for r in rs),
                    "verified": sum(r["recognition_verified"] for r in rs)}
    for kind in ("self_reported", "verified"):
        for other in ("R", "M"):
            a, b = recog["T"], recog[other]
            recog[f"fisher_p_T_vs_{other}_{kind}"] = float(fisher_exact(
                [[a[kind], a["n"] - a[kind]], [b[kind], b["n"] - b[kind]]]).pvalue)

    stab = {}
    for r2 in range(2, RUNS + 1):
        pairs = [(by_run[1][p]["label"], by_run[r2][p]["label"]) for p in by_run[1]
                 if p in by_run[r2]]
        stab[f"run1_vs_run{r2}"] = {
            "n": len(pairs), "exact_agreement": float(np.mean([a == b for a, b in pairs]))
            if pairs else None,
            "recognized_agreement": float(np.mean([by_run[1][p]["recognized"] ==
                                                   by_run[r2][p]["recognized"]
                                                   for p in by_run[1] if p in by_run[r2]]))
            if pairs else None}

    a1 = agree(rows)
    lo, hi = a1.get("kappa_ci95", [float("nan")] * 2)
    v1 = ("moderate_or_better_agreement" if lo > 0.4 else "poor_agreement" if hi < 0.2
          else "inconclusive")
    a2 = strata_tests(rows)
    d_lo = a2["T_vs_R"]["cliffs_delta_ci95"][0]
    v2 = "llm_tracks_citation_label" if d_lo > 0 else "no_evidence_llm_tracks_citation_label"
    a2_unrec = strata_tests(subset(unrec))
    v2u = ("llm_tracks_citation_label_without_recognition"
           if a2_unrec["T_vs_R"].get("cliffs_delta_ci95", [0])[0] > 0 else "no_evidence")

    out = {
        "amendment": "research/preregistration_cs_breakthrough_forecast_v1_amendment3_llm_rater.md",
        "status": "reference rater only; not independent validation",
        "model": MODEL, "temperature": TEMPERATURE, "runs": RUNS,
        "items": len(items), "rated_primary": len(prim), "missing_primary": missing,
        "calls_logged": len(usage), "spend_usd_list_price": spend,
        "llm_label_distribution": {s: {str(k): sum(1 for r in rows if r["stratum"] == s
                                                   and r["llm_label"] == k) for k in range(4)}
                                   for s in NAMES},
        "recognition": recog,
        "A1_llm_vs_human": {"all": a1, "verdict": v1,
                            "recognized": agree(subset(rec)),
                            "unrecognized": agree(subset(unrec)),
                            "crosstab_including_0": crosstab},
        "A2_llm_vs_citation_label": {"all": a2, "verdict": v2,
                                     "recognized": strata_tests(subset(rec)),
                                     "unrecognized": a2_unrec, "unrecognized_verdict": v2u,
                                     "human_labeled_subset_llm": strata_tests(subset(both)),
                                     "verified_recognition_excluded":
                                         strata_tests(subset(lambda r: not
                                                             r["recognition_verified"]))},
        "A3_recognized_vs_unrecognized_llm_score": compare(
            [r["llm_label"] for r in rows if r["recognized"] and r["llm_label"] > 0],
            [r["llm_label"] for r in rows if not r["recognized"] and r["llm_label"] > 0], rng),
        "A4_stability": stab,
        "seed": SEED, "reps": REPS,
    }
    (RES / "llm_rater_analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"rate": rate, "analyze": analyze}[sys.argv[1]]()
