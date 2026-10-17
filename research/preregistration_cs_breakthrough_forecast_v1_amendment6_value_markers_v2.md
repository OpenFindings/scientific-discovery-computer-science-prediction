# Amendment 6 to the CS breakthrough forecast preregistration (v1): expanded value-marker study

Frozen: 2026-10-17, **before any search of the new papers**. Amendment 5 was underpowered: primary
markers were found for 4/40 citation top-decile papers and 1/40 random papers. Amendment 5's
results stay as they are. This study adds papers and pools them with wave 1. Markers, exclusions,
isolation audit and mechanical verification are identical to amendment 5.

## Sample (frozen; `scripts/run_cs_value_markers_v2.py sample`, seed 20261018)

- **T:** every remaining citation top-decile paper (64 new; T total 104, all top-decile papers
  in the 929-paper OpenAlex frame).
- **M:** the 100 citation negatives with the highest Paper 3 model score among the 497 scored
  negatives. 54 are new; 40 were wave 1's M; 6 were already in wave 1's R and keep their R label.
  M total is 94.
- **R:** a seeded random sample of the remaining citation negatives (not in the model top 100,
  not in wave 1), enough to bring R to 200 (160 new).
- The 278 new papers are shuffled with the seed and split into 14 batches of up to 20. Searchers see
  only arXiv id, year and title. Strata live only in `results/cs_forecast_v1/value_sample_v2.json`,
  which falls under the isolation audit (any access to `results/` or `cs_forecast` discards the
  batch).

Power, rough: at 10% vs 2.5% (wave-1 rates), 104 vs 200 gives about 70–80% power for C1 at α = 0.05.

## Procedure changes from amendment 5 (frozen)

- Searchers must run at least two separate web searches per paper and report a `searches` count
  per paper. Not verifiable; reported descriptively (C5).
- Items flagged "not searched in depth" are re-searched once by one fresh subagent before
  verification, as in amendment 5 addendum 1. The list is taken mechanically from the notes.
- Agents are launched in waves of up to 7. Batch 14 has 18 papers.

## Analyses (frozen; pooled waves 1 + 2 unless stated; bootstrap 10,000, seed 20261017)

- **C1 (primary):** V rate (≥1 verified M1–M3) in T vs R: risk difference CI, Fisher p.
- **C2:** V rate in M vs R.
- **C3:** among all searched citation negatives (M and R) that have a model score: AUROC of the
  Paper 3 score for V, bootstrap CI.
- **C4:** C1 and C2 with V4 (adds survey recognition), and C1 and C2 on wave 2 only (wave 2 used
  the stronger search-effort instruction).
- **C5:** mean reported searches per paper by stratum (wave 2).

## Interpretation (frozen; as amendment 5)

- C1: RD lower bound > 0 → the citation label agrees with documentary value. RD upper bound
  < 0.10 → it does not. Otherwise inconclusive.
- C2 and C3: RD lower bound > 0, or AUROC lower bound > 0.5 → the structure model finds documented
  value that citations miss. Otherwise no evidence.
- Caveats carried over: markers are partly popularity-driven, recall is imperfect and may favour
  famous papers, the evidence window is any date, and the marker type is the searcher's call.

## Budget

At most 14 searcher subagents, plus one supplementary searcher and one re-run per discarded batch.
No paid API.

Frozen hashes: `scripts/run_cs_value_markers_v2.py` `8b5f16f385a0c1ca9fc52d2e3fc8c9e54b04fe7ddd47097c9022cb42ab399f03`; `results/cs_forecast_v1/value_sample_v2.json` `01ab3310c452cfc5b87c0894213aa56f08fb1fdb43942d1dff5f8f48e80dbcb0`.

## Addendum 1 (2026-10-17, after batches 2–7 returned, before any verification or analysis)

The seven concurrent searchers shared a 200-call web-search budget per orchestrator turn. Searchers
in batches 3, 5 and 7 left most items unsearched, and most batch-4 items got only one search.
Batch 1 stopped on a usage limit before handing back and was asked to hand back its answer
unchanged. Changes, all stratum-blind:

- **Re-search list:** 58 items whose note mentions "not searched", "not assessed", "budget",
  "limit ran out" or "unverified", or whose reported searches is 0. The list is taken mechanically
  from batches 2–7 and recorded in `SUPPLEMENT` in the script. These items are re-searched in
  supplementary batches 101–103, same instructions.
- **Merging:** for re-searched items, claims from both searches are pooled (union) before
  verification. Some items found evidence before the budget ran out, and replacing their entries
  would discard verified evidence.
- **Concurrency:** at most 2 searchers run at a time from here on (batches 8–14 and 101–103).
  Batches 8–14 are screened against the same rule after they return.
- **Budget:** amendment 6 allowed 14 searchers plus one supplementary searcher. It is extended to
  14 + 3 supplementary searchers + up to 2 more if batches 8–14 trigger the rule.
