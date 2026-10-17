# Amendment 2 to the CS breakthrough forecast preregistration (v1): G3 analysis

Frozen: 2026-10-17, after the labeler exported labels but **before the labels were joined with
the stratum key** (`results/cs_forecast_v1/labeling_key.json`). The parent protocol defined G3 only
as "agreement between the citation label and the human breakthrough judgement"; this fixes how.

## Data

- Labels: one labeler (project owner), blinded page `labeling/cs_breakthrough_labeling.html`,
  export `data/cs_forecast/human_labels_v1.json` (82/120 items labeled; labeler stopped from
  fatigue). Scale: 3 breakthrough, 2 significant, 1 incremental, 0 can't judge.
- Items were shown in a seeded random order mixing three strata of 40 (`scripts/build_labeling_html.py`):
  T = citation top-decile; R = random citation-negative; M = citation-negative papers the Paper 3
  model ranked highest. Unlabeled items are the tail of that random order, so missingness is by
  design unrelated to stratum; per-stratum labeled counts are reported.
- Label 0 is excluded from tests and counted.

## Analyses (frozen)

- **G3a (primary, label validity / H3):** T vs R on the 1–3 scale. Cliff's δ (P(T>R) − P(T<R))
  with a 95% bootstrap interval (10,000 resamples within strata, seed 20261017) and a two-sided
  Mann–Whitney U p-value.
- **G3b:** share labeled ≥ 2 and share labeled 3 in T vs R, Fisher exact two-sided p.
- **G3c (H1 vs H3 disagreement):** M vs R, same statistics as G3a. Tests whether papers the
  structure model favours but citations do not are judged more valuable than random negatives.

## Interpretation (frozen)

- G3a δ lower bound > 0 → the citation label tracks human value judgement (H3 not supported).
  δ upper bound < 0.2 with lower bound ≤ 0 → H3 favoured (label mostly visibility).
  Otherwise inconclusive.
- G3c δ lower bound > 0 → structure features capture value the citation label misses (partial
  support for H1 as a *value* forecast despite G2). Otherwise no such evidence.

## Limitations stated in advance

Single labeler, no inter-rater reliability; the labeler may recognise famous papers, and fame is
itself correlated with citations, which biases G3a towards agreement. 82/120 coverage reduces
power. Results are exploratory evidence on label validity, not independent validation.
