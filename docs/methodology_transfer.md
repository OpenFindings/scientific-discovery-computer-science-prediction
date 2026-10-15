# Methodology transfer: Papers 3 and 4 to computer science

## Objective

This project applies the two published methodologies to specific,
 falsifiable computer-science questions. It is not a claim that either method
already transfers successfully, and it is not a new generic research-agent
architecture.

## What is preserved

Paper 3 is preserved as a historical, temporally frozen question-outcome
forecasting baseline. Paper 4 is preserved as an offline, typed-evidence,
next-action planning baseline. Their original outcomes, temporal split logic,
provenance requirements, utility components, and negative-result policy remain
separate from the new execution layer.

## What is adapted

| Component | Original setting | Computer-science adaptation | Required safeguard |
|---|---|---|---|
| Question universe | Astronomy questions | Versioned CS questions extracted from limitations, conflicts, replications, and benchmark gaps | Every question cites source text and publication version |
| Evidence corpus | Astronomy metadata/evidence | OpenAlex, Semantic Scholar where permitted, Crossref, arXiv, DBLP, OpenReview, ACL Anthology, and public artifacts | Store identifiers, dates, provenance, license, and duplicate links |
| Outcomes | Future attention, resolution, premise revision | Same three outcomes, with CS-specific operational labels | Blind adjudication and citation-graph/full-text sensitivity |
| Evidence graph | Scientific evidence records | Papers, datasets, code, benchmarks, claims, hypotheses, experiments, and results | Explicit independence groups and raw observation retention |
| Action planner | Offline historical action ranking | Same ranking plus an optional constrained executor | Score planning separately from realized execution |
| Execution | Not part of Paper 4 | Allow-listed, shell-free, reproducible pilot executor | Failed and timed-out actions remain first-class evidence |

## Evaluation matrix

The minimum comparison is random selection, citation ranking, trend ranking,
Paper 3 alone, Paper 4 alone, and Paper 3 + Paper 4 under matched budgets.
Question-level forecasting and action-level planning must be reported
separately. The historical cutoffs 2016-12-31, 2018-12-31, and 2020-12-31 are
candidate CS snapshots; each horizon is valid only when its future outcomes are
observable.

## Current implementation boundary

This worktree now contains a broad arXiv `cs.*` metadata/abstract harvest
(937,531 unique titled records, 2010–2026) and a separate partial OpenAlex
sample. It also implements a deterministic controlled pilot with typed
questions, hypotheses, evidence, graph provenance, Bayesian updates, a
cost-aware planner, safe execution, and raw-output-preserving interpretation.
It does not yet contain a full-text-coded question corpus, the Paper 3 feature
extractor, a Paper 4 reference-estimator import, historical labels, or a
validated 20-question opportunity map. Results from the four-case pilot
therefore validate only infrastructure behavior and must not be presented as
transfer evidence. The arXiv harvest is only a retrieval frame, not a corpus
that has been fully read or analyzed for research claims.

## Claims policy

Every dashboard and manuscript result must distinguish:

- verified observation;
- model forecast;
- planner recommendation; and
- realized experimental result.

No candidate is called “underexplored” from citation counts alone. No Paper 3
or Paper 4 transfer claim is made until the historical, grouped, leakage-safe
evaluation succeeds and negative results are reported.
