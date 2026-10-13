# Paper 4 methodology

## Scope and source status

This document describes the reproducible baseline from Paper 4, *Planning the
Next Evidence Acquisition Step: An Offline Framework for Active Scientific
Discovery*. The source repository supplied for this project is:

<https://github.com/nonameisready/scientific-evidence-planner>

The exact paper URL must be resolved by title and pinned before publication;
this project must not invent a publication identifier. The local audit records
Paper 4 as an offline planner: it ranks evidence-acquisition actions from
static inputs and does not execute agents, browsers, instruments, or research
experiments.

## Baseline workflow

The canonical workflow is:

`question -> competing hypotheses -> typed evidence graph -> gap analysis -> candidate actions -> expected utility -> best next action -> Bayesian evidence update`

The graph represents papers, datasets, observations, claims, hypotheses,
experiments, and artifacts with typed relations and provenance. Evidence
records retain confidence and source-independence information. Gap analysis
identifies missing, weak, contradictory, or insufficiently independent support.

Candidate actions may reproduce an experiment, run an ablation, evaluate an
alternative dataset, test a contradictory hypothesis, construct a controlled
benchmark, vary parameters, validate across domains, or investigate an
unexpected failure.

The utility model combines:

- expected information gain;
- provenance-based novelty/independence;
- tractability; and
- research cost.

Weights are configurable. Bayesian updating uses the declared action outcome
likelihoods; likelihoods must not be guessed implicitly from an observation.
The historical evaluation reports top-K utility, entropy reduction, average
information gain, action diversity, hypothesis coverage, resolution efficiency,
and expected utility.

## Validity constraints

Expected utility is a planning estimate, not demonstrated scientific value.
Historical action-level ground truth may be unavailable; in that case only
question-level forecasting should be scored. Any attention-versus-utility
claim must control for evidence breadth, research area, question specificity,
publication age, benchmark availability, and retrieval coverage.

The local audit records that the original scaled-benchmark neglect finding was
withdrawn after blind citation-graph re-adjudication. Therefore, Paper 4 must
not be used to assert that a question is neglected merely because retrieval
found no directly addressing paper. Retrieval failure and evidence breadth are
measurement risks that belong in the result and uncertainty record.
