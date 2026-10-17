# Amendment 7 to the CS breakthrough forecast preregistration (v1): posting-time cutoff and value prediction

Frozen: 2026-10-17, **before either analysis is run**. Paper 4's re-ranking selected these two
analyses (`reports/paper4_cs_forecast_update_and_rerank_v2.json`; B1 and B5). Neither analysis
needs new data. The primary results (G1–G4) are unchanged.

## Z: forecast at posting time (B1, targets H2)

**Question:** with no citation information at all, i.e. at the moment of posting, do Paper 3
structure features forecast the same top-decile outcome beyond the baselines still available?

**Cutoff change:** every feature must be computable at posting.
- `env_topic_volume_log` and `env_topic_growth` are recomputed from year *y−1* (volume in *y−1*;
  growth *(y−1)/(y−3)*), because year-*y* totals include papers posted later in *y*.
- `base_cites_year0_log` and `base_months_to_cutoff` are dropped. The citation-trend baseline
  therefore cannot be computed and is removed.
- Unchanged: text, falsifiability and tractability features (benchmark availability stays at
  year *y*, a small stated leak for papers posted early in *y*), references with year ≤ *y*,
  prior topic-pair counts (before *y*), earlier-year retrieval features, and author prior works
  (before *y*).
- **Remaining baselines:** publication count (topic volume *y−1*, author prior), research trend
  (growth *y−1*), simple statistical (number of references, words, authors), and TF-IDF kNN.

**Outcome, models and validation:** identical to the primary (same `y_breakthrough`, rolling
origin over 2016–2022, 3-year embargo, logistic as primary, 2,000 cell-bootstrap replicates with
seed 20261014).

**Gates:**
- **Z1:** Paper 3 pooled AUROC lower 95% bound > 0.50.
- **Z2:** combined (Paper 3 + posting-time baselines) minus the best posting-time baseline (best
  chosen on pooled AUROC) ΔAUROC lower 95% bound > 0.
- If Z2 passes, structure adds forecast value when momentum is unavailable. That is a timing
  claim: it does not overturn G2, which tests the year-end cutoff.
- **Descriptive:** the Paper 3 AUROC at posting vs at year-end, and the year-end citation-trend
  AUROC, to show how much momentum adds.

## D: does the structure score predict documentary value? (B5, targets H1 as a value forecast)

**Data:** the 398 papers searched in amendments 5–6, with V (≥1 verified M1–M3 marker). Only
papers in test years 2016–2022 have out-of-time scores (`results/cs_forecast_v1/predictions_primary.csv`).

**Analyses:**
- **D1:** AUROC of the out-of-time Paper 3 logistic score for V.
- **D2:** the same for the out-of-time citation-trend baseline score.
- **D3:** paired difference D1 − D2.
- Intervals come from 10,000 paper-level bootstrap replicates, seed 20261017. The sample is
  stratified (all top-decile papers, model top-100 negatives, random negatives), so these are
  within-sample discrimination statistics, not population estimates.
- **Sensitivity:** D1–D3 with inverse-probability weights for the random stratum (pool size / 200).

**Gates:**
- D1 lower bound > 0.5 → the structure score tracks documentary value.
- D3 lower bound > 0 → structure beats citation momentum at predicting documentary value.
- V is rare, so wide intervals are expected. The number of positives is reported.

## Code

`scripts/run_cs_posting_cutoff_and_value.py` is committed with this file before it is run.

Script sha256 at freeze: `3977046bfc7b90c57772cd8fe883eb636618ceb5ff03cae760c1150b704ef746`.
