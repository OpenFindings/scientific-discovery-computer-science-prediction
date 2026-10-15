# Amendment 1 to the CS breakthrough forecast preregistration (v1): cross-source label check

Frozen: 2026-10-15, before any outcome analysis. Parent protocol:
`research/preregistration_cs_breakthrough_forecast_v1.md` (unchanged by this amendment).

## State of knowledge at freezing

- OpenAlex responses for ~800/1,006 frame papers are cached (archive
  `data/cs_forecast_cache/openalex_cache_20261015.tar.gz`). They contain per-year citation counts,
  but **no outcome has been computed, tabulated or inspected**. `scripts/run_cs_forecast.py` has
  not been run on real data (only its unit tests).
- No Semantic Scholar (S2) citation data has been retrieved. A coverage probe on 30 frame papers
  (seed 20261015) checked record existence only: 9/9 non-throttled lookups were found; 21 were
  rate-limited. No counts were read.

## What this amendment adds and does not change

Adds a **secondary** analysis testing one form of H3 (label artifact): that the primary label
`y_breakthrough` reflects which bibliographic database counts the citations (coverage,
version merging, year errors) rather than the paper. It does **not** change the primary outcome,
features, baselines, validation design, metrics or gates G1–G3. All features stay OpenAlex-derived.
S2 data is used only as an alternative outcome.

## Competing explanations for any disagreement

1. Coverage: one database misses citing venues or citing works.
2. Version handling: preprint and published versions merged in one database, split in the other.
   OpenAlex counts are pooled over all exact-title-matched records; S2 merges versions itself.
3. Year assignment: a citing work dated by preprint year in one source, venue year in the other.
4. Retrieval timing: the two snapshots are taken days apart; minor, since all windows end ≤ 2025.

## Data and outcome (frozen)

- Source: S2 Academic Graph API, `POST /graph/v1/paper/batch` with ids `arXiv:<id>`, then
  `GET /graph/v1/paper/{paperId}/citations?fields=year,externalIds&limit=1000` paginated to the end.
  No versioned snapshot exists; per-request UTC retrieval times are recorded in a manifest.
- `cites_3y_s2` = distinct citing S2 papers whose `year` is in *y+1 … y+3* (*y* = publication year
  from the frame, same as primary). Citing papers with null `year` are excluded from the count and
  their number is reported per paper.
- `y_breakthrough_s2` = `cites_3y_s2` ≥ the 90th percentile of `cites_3y_s2` among S2-matched frame
  papers of the same publication year (identical rule to the primary label).

## Analyses (frozen)

Run once, on papers matched in **both** sources (the "joint set"):

- S1 label agreement: Cohen's κ between `y_breakthrough` and `y_breakthrough_s2`; also raw
  agreement and the share of OpenAlex positives that are S2 positives.
- S2 count agreement: Spearman ρ between `log1p(cites_3y)` and `log1p(cites_3y_s2)`.
- S3 forecast robustness: rerun the primary rolling-origin scoring with target `y_breakthrough_s2`
  and the same predictors; report G1/G2 under this label next to the primary result.

Uncertainty: 95% intervals from 2,000 bootstrap replicates resampling frame year×topic cells, seed
20261014 (the primary's resampler, `cs_forecast.evaluate.cluster_bootstrap` or the same cell
scheme for κ and ρ).

## Falsification gate (G4, label source-robustness)

- **Robust:** κ lower 95% bound ≥ 0.60.
- **Source-dependent:** κ point estimate < 0.40. Then any primary-label conclusion is reported as
  database-specific, and "breakthrough" wording stays barred regardless of G3.
- **Inconclusive:** anything else; reported as such.
- If G1 or G2 passes under one label and fails under the other, the primary result stands as
  preregistered but is reported as source-sensitive.

These thresholds are conventional κ bands, chosen before data, not tuned.

## Exclusions, budget and storage

- Papers not found in S2, or with an S2 error after retries, are excluded from S1–S3 and counted.
  If S2 coverage of OpenAlex-matched papers is < 90%, the coverage gap is reported as a limitation
  next to every S1–S3 number.
- Budget: ≤ 6,000 S2 requests; ≤ 1 request/second; exponential backoff on 429/5xx; no paid calls.
  The S2 key is read from `S2_API_KEY`, sent as the `x-api-key` header, and never written to disk.
- Raw S2 responses are cached locally and git-ignored. Only derived per-paper counts
  (`cites_3y_s2`, null-year count, S2 paperId) are committed, subject to the S2 API License
  Agreement accepted by the account holder.

## Order of operations

1. Commit this amendment (done before any outcome is computed).
2. Write and commit the S2 fetch and the S1–S3 analysis code before running them.
3. Complete the OpenAlex fetch; run the primary analysis as preregistered.
4. Run the S2 fetch, then S1–S3 once. Report all results, including nulls, without revising
   thresholds.
