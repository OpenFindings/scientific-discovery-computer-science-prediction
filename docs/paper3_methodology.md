# Paper 3 methodology

## Scope and source status

This document is a reproducibility-oriented transfer note for Paper 3,
*What Makes a Scientific Question Succeed? Predicting Future Attention,
Resolution, and Premise Revision from Question Structure and Evidence Context*.
The source repository supplied for this project is:

<https://github.com/nonameisready/scientific-question-outcome-prediction-indicators>

The exact repository contents and the published paper should be pinned and
archived before a final result is claimed. The local audit records the following
method as the verified baseline for this worktree.

## Baseline design

Paper 3 uses a temporally frozen astronomy corpus. It contains 980 questions,
five historical cutoffs (2012, 2014, 2016, 2018, and 2020), eight astronomy
subfields, four question-generation sources, an eight-year pre-cutoff evidence
window, and a five-year future observation window. The underlying deduplicated
metadata corpus covers 2005--2025 and 313,189 papers.

For every question and cutoff, features are computed only from information
available by that cutoff. The feature families are:

1. question structure;
2. pre-cutoff evidence context;
3. novelty;
4. falsifiability;
5. tractability; and
6. environmental controls.

Future outcomes are separately labelled for future attention, scientific
resolution, and premise revision. Candidate future records are retrieved and
the outcome is adjudicated by a blinded judge; premise-refutation cases receive
an independent second judge and a random audit sample.

## Evaluation protocol

The baseline must use temporal validation rather than random splits. The
reported analyses include temporal split, leave-one-subfield-out,
cross-domain, ablation, controlled-effect, and stability analyses. Reported
reference results include temporal AUC 0.71, cross-domain AUC 0.71, and
leave-one-subfield-out AUCs of 0.62--0.78. These are astronomy results and are
not expected values for computer science.

The computer-science transfer must compare the Paper 3 feature model with at
least publication-count, historical-citation, text-embedding, research-trend,
and simple statistical baselines. Primary metrics are AUROC, AUPRC, Brier
score, calibration, ranking quality, and temporal generalization. Related
questions and repeated snapshots must remain in the same validation group.

## Transfer rules

- Freeze each historical snapshot before computing features or labels.
- Never use present-day citation counts or future publications as historical
  features.
- Keep attention, resolution, and premise revision as separate outcomes.
- Treat Paper 3 feature weights as a transfer condition, not ground truth.
- Report null and negative results.
- Do not use a low citation count as a neglect label without retrieval and
  citation-graph sensitivity checks.

The structure-prior results recorded in the local audit are hypotheses for
computer-science testing: review recognition, directly related prior evidence,
explicit competing hypotheses, cluster breadth, and explicit contradiction may
be predictive. Their astronomy-derived effect sizes must not be copied into a
computer-science model without validation.
