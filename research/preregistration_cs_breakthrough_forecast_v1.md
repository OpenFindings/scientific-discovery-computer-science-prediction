# Preregistration: CS breakthrough forecasting with Paper 3 features (v1)

Frozen: 2026-10-14, before any outcome or OpenAlex data for the frame was retrieved in this
campaign. This is a new direction; it does not reuse the earlier 13-question labeling task or
findings 155–158.

## Question

Can cutoff-time structural features of a computer-science paper's research question and evidence
context (Paper 3 feature groups A–F, adapted to CS) forecast which papers become *breakthrough
candidates* — top-decile future attention — better than simple publication-count,
citation-trend, text-similarity, research-trend and statistical baselines, under strictly
time-ordered validation?

## Competing hypotheses (Paper 4 structure)

- **H1 structure signal.** Paper 3 features carry out-of-time signal beyond baselines.
- **H2 momentum only.** Any signal is reducible to early citations / topic growth.
- **H3 label artifact.** Top-decile citation attention tracks visibility (surveys, hype topics,
  citation splitting across versions), not breakthrough contribution.
- **H4 no signal.** Nothing beats random out of time.

## Units and data

- Unit: one unique arXiv paper from `data/historical_cs_year_topic_frame.jsonl` (1,006 unique
  papers, publication years 2010–2022). Multi-topic duplicate rows are collapsed to the first
  row. Cutoff = 31 Dec of publication year *y*.
- Source of features and outcomes: OpenAlex (CC0), retrieved once and cached; retrieval date is
  recorded. Nothing else is downloaded. No full texts are fetched.

## Outcome (frozen)

- `cites_3y` = number of distinct OpenAlex works citing the paper (any of its matched OpenAlex
  records) whose publication year is in *y+1 … y+3*. All windows end by 2025, so all are
  mature on 2026-10-14.
- **Primary label `y_breakthrough`**: `cites_3y` ≥ the 90th percentile of `cites_3y` among frame
  papers of the same publication year.
- Secondary: (a) same label after excluding survey/review/tutorial papers (title/abstract rule);
  (b) Spearman correlation between score and `log1p(cites_3y)`.
- This is an **attention proxy**, not proof of a breakthrough. Its validity is tested separately
  with blinded human labels (H3).

## Features (cutoff-time only)

- A text: CS-adapted Paper 3 regexes on title+abstract.
- B evidence context: references with publication year ≤ *y* only (count, age, recency, topic
  diversity, review share); similarity to earlier-year frame papers.
- C novelty: nearest-neighbour distance to earlier-year frame papers; prior co-occurrence count
  of the paper's OpenAlex topic pairs before *y*; reference field breadth.
- D falsifiability: rule-based markers (no LLM).
- E tractability (CS): named benchmarks released by the cutoff, artifact/code release, new
  benchmark/dataset introduced, hardware, compute scale, human study, formal proof, empirical
  evaluation, deployment.
- F environment: OpenAlex primary-topic publication volume in *y* and growth *y/(y-2)*.
- Excluded from Paper 3 model: the paper's own citations, author identities, venue (venue may be
  assigned after the cutoff).

## Baselines (frozen)

1. random (constant score);
2. publication count: topic volume + authors' prior publication counts (works before *y*);
3. citation trend: the paper's own citations received within year *y* + months since posting +
   topic growth;
4. text similarity: TF-IDF k-nearest-neighbour (k=15, cosine) label mean from training papers;
5. research trend: topic growth alone;
6. simple statistical: reference count, abstract length, author count.

Models: logistic regression (standardized, L2, C=1.0, median imputation) is primary;
gradient boosting (300 trees, depth 3, lr 0.05, seed 7) is a sensitivity analysis. No
hyperparameter tuning.

Combined model = Paper 3 features + all baseline inputs.

## Validation (frozen)

Rolling origin with label embargo: for each test year *t* ∈ 2016…2022, train on papers with
*y* ≤ *t*−3 (labels knowable by 31 Dec *t*), test on *y* = *t*. Predictions pooled over test years.
Random splits are not used. Additional: leave-one-frame-topic-out (sensitivity only).

## Metrics and uncertainty

AUROC (primary), AUPRC, Brier, expected calibration error (10 bins), precision at top 10%,
Spearman with `log1p(cites_3y)`. 95% intervals from 2,000 bootstrap replicates resampling
frame year×topic cells (seed 20261014); paired differences use the same replicates.

## Falsification gates

- **G1 (signal):** Paper 3 model pooled AUROC lower 95% bound > 0.50. Fail → H4 favoured for
  structure features.
- **G2 (incremental value):** Combined minus best single baseline (best chosen on pooled test
  AUROC, which favours the baseline) ΔAUROC lower 95% bound > 0. Fail with G1 pass → H2
  favoured.
- **G3 (label validity, H3):** blinded human labels on a Paper 4-prioritized sample; reported
  as agreement between the citation label and the human breakthrough judgement. Not required
  for G1/G2 but required before calling any forecast a "breakthrough" forecast.
- Forward forecasting of current directions is attempted only if G1 and G2 pass.

## Exclusions and budget

Papers without an OpenAlex match are excluded and counted. Budget: ≤ 15,000 OpenAlex
requests, no paid model calls. Null and negative results are reported as is.

## Implementation corrections (append-only)

- 2026-10-16, before `scripts/run_cs_forecast.py` was first run on real data and before any
  outcome was computed: 164/929 matched papers have an OpenAlex authorship with no author id.
  The fetch issued `author.id:None` (HTTP 400, the run's only error) and the feature code counted
  that authorship as an author with 0 prior works, lowering `base_author_prior_mean_log` (a
  publication-count baseline input; not a Paper 3 feature). Corrected to treat it as missing,
  consistent with "authors' prior publication counts". No outcome, threshold or gate changed.
