# Amendment 8: prospective registered forecast for 2025 CS papers

Frozen: 2026-10-17, **before any 2025 paper is sampled or fetched**. Every earlier analysis in this
project is a backtest. This amendment registers forecasts whose outcomes do not exist yet in
full, and that cannot be evaluated before 2029.

## Cohort (frozen)

- **Pool:** OpenAlex works with `publication_year:2025`, primary location arXiv
  (`S4306400194`), primary topic field Computer Science (`fields/17`). 55,016 works on 2026-10-17.
- **Candidates:** OpenAlex `sample=1000`, `seed=20261017`, retrieved in pages of 100.
- **Eligibility,** in sample order, keeping the first **700** eligible papers:
  - the DOI resolves to an arXiv id (`10.48550/arxiv.<id>`);
  - the arXiv API shows the first version posted in 2025;
  - no arXiv version was posted after 2025-12-31, so the text is the cutoff-time text. This is
    the same rule as the historical frame.
  - Ineligible counts are reported.
- **Cell:** OpenAlex primary-topic subfield, used for the bootstrap clusters.

## Features (frozen; cutoff 2025-12-31)

Same code as the primary analysis (`cs_forecast.features.paper_features`, `retrieval_features`).
Differences, all stated now:

- **Citations:** only the 2025 citation count is retrieved (`cites:<id>,publication_year:2025`,
  read from `meta.count`). No per-year citation breakdown and no citation data from 2026 or
  later is downloaded before evaluation.
- **No title-search version merging at registration.** The DOI record is used. Version merging is
  done at evaluation and applied the same way to every paper.
- **Retrieval features** compare each 2025 paper with the 929 historical frame papers (all
  earlier years). There are no 2023–2024 frame papers, which is a stated distribution shift.
- Topic volume, topic growth, topic-pair priors and author prior works are computed as in the
  primary analysis.

## Models (frozen; no tuning)

Trained on all 929 historical frame papers with their primary label `y_breakthrough`; every label
matured by 2025. Model specifications are identical to the primary analysis.

**Registered scores per paper:**
- `paper3_cs_logistic` (primary) and `paper3_cs_gbm`;
- `combined_logistic`;
- the baselines `citation_trend`, `publication_count`, `research_trend`, `simple_statistical`,
  `text_similarity_knn` and `random`;
- a posting-time variant (amendment 7 feature set): `posting_paper3_cs_logistic` and
  `posting_combined_logistic`.

## Registration

Predictions are written to `results/prospective_2025/predictions.csv` and their SHA-256 is written
to `results/prospective_2025/manifest.json`. Both are committed and pushed in one commit before any
outcome is retrieved; the GitHub push records the time. Predictions are never edited afterwards.
A rerun with the same inputs must reproduce the file hash.

## Outcome and evaluation (frozen; run on or after 2029-04-01)

- `cites_3y` = distinct OpenAlex works citing any exact-title version of the paper, published in
  2026–2028, retrieved on or after 2029-04-01 to allow for indexing lag.
- **Label:** `cites_3y` ≥ the 90th percentile within the cohort.
- **Metrics:** AUROC, with 2,000 bootstrap replicates resampling subfield cells, seed 20261014.
- **Gates:**
  - **P1:** `paper3_cs_logistic` AUROC lower 95% bound > 0.50.
  - **P2:** `combined_logistic` minus the best year-end baseline, ΔAUROC lower bound > 0.
  - **P3 (posting time):** `posting_combined_logistic` minus the best posting-time baseline
    (`publication_count`, `research_trend`, `simple_statistical`, `text_similarity_knn`), ΔAUROC
    lower bound > 0.
- **Expected from the backtests (stated now, not a gate):** P1 passes, P2 and P3 fail.
- Evaluation code: `scripts/prospective_2025_evaluate.py`, committed now and refusing to run
  before 2029-04-01.

## Budget

OpenAlex requests ≤ 9,000 (free key), arXiv API ≤ 15 requests. No paid calls.

Code sha256 at freeze: `scripts/prospective_2025_register.py` `2e4086b5a46b31137ad937ad058e7e2236086d139c7300e2be383c6390d0d663`; `scripts/prospective_2025_evaluate.py` `948fd21cdc2d8aad6e7f64ce9b1b6de4e9c8f8174e2c84412e685a7726203550`.

## Addendum 1 (2026-10-17, after the feature fetch, before any model is trained or prediction made)

**Blocker found:** OpenAlex has no references for any of the 700 cohort papers. Every record has
`referenced_works` empty; for example `W4417264343` has `referenced_works_count` 0. The historical
training frame has references for 791 of 929 papers. Predicting with empty reference features
would remove the strongest Paper 3 group (the evidence-context group, 0.752 alone) and the
reference count used by the simple-statistical baseline, and the test would be meaningless.

**Change (fixed now, before any prediction):** reference lists for **both** the 929 training
papers and the 700 cohort papers come from Semantic Scholar
(`/graph/v1/paper/arXiv:<id>?fields=references.title,references.year,references.externalIds`;
key `S2_API_KEY`; at most 1 request per second; raw responses cached and git-ignored). Training
and prediction therefore use one reference source.

- **Reference fields:** year and title from S2. Topic and field come from OpenAlex, looked up by
  DOI in batches of 50; arXiv references use DOI `10.48550/arxiv.<id>`. An unmatched reference
  has topic and field null. Only references with year ≤ cutoff year count, as before.
- A paper with no S2 references gets an empty list, the same as historical papers without
  OpenAlex references.
- **Every model is retrained** on the S2-reference version of the 929 training papers. All other
  features are unchanged.
- **Descriptive comparability check, not a gate:** on the 929 historical papers, report the
  correlation of `ev_n_refs` between the OpenAlex and S2 sources, and the rolling-origin backtest
  AUROC of `paper3_cs_logistic` with S2 references next to the primary 0.654.
- The registered predictions use only the S2-reference models. The OpenAlex-reference primary
  results (G1–G4) are unchanged.
- Code updated for addendum 1 before any prediction: `scripts/prospective_2025_register.py` sha256 `21801200448b2b4a2740d6d1a3915d0382552bc847976a394160e7810c563175`; new `scripts/prospective_2025_s2_refs.py`.
