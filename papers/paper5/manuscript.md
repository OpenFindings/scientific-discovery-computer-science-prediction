# Forecasting and Prioritizing Computer Science Research Opportunities Through Scientific Question Prediction and Evidence-Guided Planning

## Abstract

This study specifies an empirical transfer evaluation of two existing
methodologies: Paper 3's temporally grounded prediction of future scientific
question outcomes and Paper 4's offline planning of the next evidence
acquisition action. We apply them to versioned, source-cited computer-science
questions and compare them with popularity and trend baselines. The repository
currently contains an executable infrastructure pilot, bounded real-DBMS
guidance checks, a full-arXiv-CS
metadata/abstract harvest, and an initial set of 26 source-linked question
candidates, but no full-text-coded question corpus or audited historical
labels. Consequently, this manuscript is a
registered methods and application protocol, not a claim of successful
transfer.

## 1. Research questions

1. Do Paper 3 question and evidence-context features predict future attention,
   resolution, or premise revision in computer science?
2. Does evidence structure identify actionable uncertainty beyond popularity
   and trend baselines?
3. Does Paper 4's next-evidence ranking reduce uncertainty under matched cost?
4. Which opportunities remain on the Pareto frontier across significance,
   uncertainty, tractability, reproducibility, and cost?

## 2. Methods

### Discovery corpus collected for screening

The arXiv discovery corpus contains 937,531 unique titled records matching
`cat:cs.*`, submitted from 2010-01-01 through 2026-10-11. All 937,538 quarterly
API result slots were retrieved and audited across 68 date windows. Abstract
and PDF-link coverage are 100% in the harvested records. Of the unique records,
816,895 have a CS primary category and 120,636 are cross-listed into CS with a
non-CS primary category; analyses must preserve that distinction. The corpus
is metadata plus abstracts and links, not 937k downloaded/read full texts, and
does not cover venue papers absent from arXiv. A separate OpenAlex sample has
9,746 titled works from 13 of 18 planned topic queries; it is incomplete and
has not been merged. Collection and audit details are in
`docs/literature_collection.md` and `data/arxiv_cs_manifest.json`.

This discovery corpus is a retrieval frame only. The study dataset will be a
smaller, source-adjudicated set of specific questions extracted from paper
limitations, conflicting findings, replications, and benchmark gaps. No
forecast, historical label, or research-opportunity result is inferred from
the raw corpus counts.

### Evaluation methods

Question records contain a canonical question, domain, historical cutoff,
feature snapshot, source provenance, evidence independence groups, and audited
future labels. The Paper 3 transfer keeps the three outcomes separate and uses
temporal grouped validation. The Paper 4 transfer represents competing
hypotheses and evidence provenance in a typed graph, ranks candidate actions by
declared information gain, novelty/independence, tractability, and cost, and
updates beliefs only with declared likelihoods.

The comparison includes random, citation, trend, Paper 3, Paper 4, and combined
Paper 3 + Paper 4 rankings under matched budgets. Outcomes are AUROC, AUPRC,
Brier score, calibration, ranking quality, entropy reduction, action diversity,
hypothesis coverage, resolution efficiency, and expected utility.

## 3. Historical validation

Candidate snapshots are 2016-12-31, 2018-12-31, and 2020-12-31, subject to the
five-year outcome being observable. Present-day citations, future publications,
and unaudited LLM labels are excluded from historical features. Action-level
ground truth is scored only where documented; otherwise evaluation is limited
to question-level outcomes.

## 4. Current status

The deterministic four-case pilot validates evidence recording, safe execution,
interpretation, Bayesian updating, and cost-aware action selection. It is not a
computer-science transfer result. The transfer runner reports the candidate
inventory and waits for full-text feature coding and historical labels before
forecasting. Separately, pinned Docker runs of SQLancer/QPG and SQLancer++
feedback on SQLite/NoREC exposed a cross-tool compatibility failure, a
zero-database run despite exit code 0, and a delayed validity-proxy response
to SQLancer++ feedback over longer runs. These are exploratory real-tool
observations, not a Paper 3/4 transfer result, agent-effectiveness estimate,
or confirmed distinct logic bug; see `docs/dbms_guidance_campaign.md`.

## 5. Limitations

Retrieval coverage, duplicate paper versions, benchmark availability, source
independence, question specificity, and label adjudication can all bias the
results. Low citation count is not treated as evidence of neglect. Forecasts
and planner recommendations are not realized scientific value.

## 6. Reproducibility

See `papers/paper5/reproducibility.md`, `docs/paper3_methodology.md`,
`docs/paper4_methodology.md`, and `docs/methodology_transfer.md`.
