# Paper 3/4 source audit for the CS direction program

Checked 2026-10-13 against the user-provided repositories at fixed commits:

- Paper 3: `nonameisready/scientific-question-outcome-prediction-indicators`
  commit `9b842fb0105c58819c4a5e6401ce984bd5b28b90`, especially
  `paper/paper3.md`, `pipeline/models.py`, `results/baselines.json`, and
  `docs/design_mapping.md`.
- Paper 4: `nonameisready/scientific-evidence-planner` commit
  `d3b61480a390a224bff9d688322f26270734c0a4`, especially
  `paper/paper.tex`, `src/planner/utility.py`, `src/planner/planner.py`,
  `configs/default.yaml`, and `configs/paper3_informed.yaml`.

These are source-repository revisions, not verified publication version IDs.
The exact OpenFindings publication URL for Paper 4 remains unresolved.

## What the results support

Paper 3's primary demonstrated prediction is **five-year substantive
attention in astronomy**. On the 2020 temporal test set its structured
logistic model has AUC 0.713; cross-subfield tests are above chance. The
strongest stable correlates include prior review recognition, directly
related evidence, and explicit competing hypotheses. The paper warns that
abstract-level retrieval misses engagement with narrow object-level
questions and that direct-LLM questions can leak hindsight. Its five-way
outcome classifier has macro-F1 0.23: only eight questions were answered and
four premises refuted among 980, so the paper does **not** establish a
reliable model for predicting resolution or premise revision individually.
Its astronomy coefficients and AUC are not CS estimates.

Paper 4 ranks possible *next evidence actions* for a supplied question,
hypotheses, and evidence graph. It combines expected entropy reduction,
provenance novelty, tractability, and cost. Its information-gain estimator
uses action-type likelihood-ratio defaults, which are assumptions requiring
CS-specific checking. The source system is offline; it does not execute the
recommended experiments. It is an action-ranking baseline, not a validated
measure of a question's scientific value.

The most consequential Paper 4 correction is its blind citation-graph audit
of 62 high-specificity questions. Among 36 originally labelled
`not_addressed`, 34 were found engaged under a lenient reading and 25 under
the strictest reading. The apparent planner-utility versus attention effect
then disappears (reported p=0.70 or 0.61 versus original p=0.004). Paper 4
explicitly withdraws the interpretation that high utility detects neglected
research. Low retrieved attention must not be turned into an opportunity
score without a stronger retrieval and adjudication audit.

## Transfer rule for this repository

1. Extract concrete, source-located CS questions and counterevidence before
   assigning an action. Keep facts, hypotheses, and proposed tests separate.
2. Preserve Paper 3's three outcome definitions, but expose **no CS outcome
   probabilities** until a source-frozen CS question cohort has audited
   future labels and passes grouped temporal evaluation against simple
   baselines. Resolution and premise revision need enough independent events
   to evaluate separately; until then report them as unvalidated targets.
3. Use Paper 4 to specify a discriminating, affordable next evidence action
   within each question. Its utility terms are planning assumptions. Record
   action likelihoods, provenance roots, and realized results before treating
   a recommendation as progress.
4. Test the strongest alternative explanation and the measurement process.
   For a claimed literature gap, this includes citation-linked/full-text
   follow-up; for an empirical effect, it includes a matched-budget or
   held-out-condition test.
5. Report a direction as a **candidate for investment** only with a source
   trail, an observable outcome, a feasible next action, and a reason to
   stop if the result or independent literature contradicts it. This is a
   decision dossier, not a Paper 3/4 performance claim.

`opportunity.py` now rejects forecast and ranking calls until a CS model and
action outcomes are validated; no hand-set coefficients remain in its live
path. The controlled four-case execution fixture is a software smoke test
and supplies no CS transfer outcome.
