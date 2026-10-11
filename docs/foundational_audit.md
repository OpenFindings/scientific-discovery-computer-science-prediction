# Foundational audit: Papers 3 and 4

Audited 2026-10-11 from the public repositories supplied by the user:

- [Paper 3 repository](https://github.com/nonameisready/scientific-question-outcome-prediction-indicators)
- [Paper 4 repository](https://github.com/nonameisready/scientific-evidence-planner), using branch `claude/evidence-planner-framework-mh6zwz` where the implementation and manuscript materials are exposed.

## Paper 3: verified methodology

Paper 3 is a temporally grounded astronomy dataset and prediction study, not an agent-execution study. It contains 980 frozen questions, five cutoffs (2012, 2014, 2016, 2018, 2020), eight astronomy subfields, four generation sources, an eight-year pre-cutoff evidence window, and a five-year future window. The corpus is the deduplicated 2005–2025 astro-ph metadata record (313,189 papers).

Feature groups are question structure, pre-cutoff evidence context, novelty, falsifiability, tractability, and environmental controls. Future outcomes use retrieved candidate records, a blinded outcome judge, and an independent second judge for premise-refutation cases plus a random sample. Evaluation forbids random train/test splits and uses temporal, leave-one-subfield-out, cross-domain, ablation, controlled-effect, and stability analyses.

The repository reports temporal-split AUC 0.71, cross-domain AUC 0.71, and leave-one-subfield-out AUC 0.62–0.78. Robust predictors include prior review recognition, directly related prior evidence, and explicit competing hypotheses; most pre-stated mechanism hypotheses were not supported.

The structure-prior addition is relevant to Paper 5: within tension-mined questions, cluster breadth predicts uptake, explicit contradiction predicts engagement, and quantified recurrent tensions were associated with resolution/refutation. These are astronomy-derived priors, not validated computer-science weights.

## Paper 4: verified methodology

Paper 4 is an offline next-evidence planner. Its workflow is:

`question -> competing hypotheses -> evidence graph -> gap analysis -> candidate actions -> expected utility -> best next action -> evidence update`

The implementation contains shared schemas, question loading, hypothesis generation, a typed graph with confidence-weighted supports/contradictions/derivations/observations, gap analysis, configurable action generation, utility estimators, ranking, Bayesian belief updates, and historical evaluation. Utility components are information gain, provenance-based novelty, tractability, and cost, with YAML-configurable weights. The repository reports seven metrics: top-K utility, entropy reduction, average information gain, action diversity, hypothesis coverage, resolution efficiency, and expected utility.

The explicit boundary is important: Paper 4 does not execute agents, browsers, instruments, or experiments. It plans from static datasets and evaluates against hidden post-cutoff historical outcomes. Paper 5's new contribution must be controlled execution and evidence ingestion under matched budgets, not a claim that the planner itself is new.

## Revision and limitation

The Paper 4 repository's later revision corrects an earlier interpretation. Paper 3's semantic novelty effect is small and positive (reported controlled beta +0.17, p=0.03) but only about 50% sign-stable; the null result is for evidence-tension density (reported beta 0.06, p=0.52). Paper 4's provenance-independence novelty term must not be justified by claiming that novelty is null.

The original scaled-benchmark neglect finding also did not survive adjudication. The repository reports blind citation-graph re-adjudication of 62 high-specificity questions: 34 of 36 originally labelled `not_addressed` were engaged under the lenient criterion, 69% under the strict criterion, and the utility effect became non-significant (reported p=0.70 lenient and p=0.61 strict, versus p=0.004 originally). The durable result is a retrieval/measurement limitation and the breadth mechanism, not the withdrawn neglect claim.

## Consequences for this project

1. The current Paper 5 pilot is not a port of Paper 4; it is an infrastructure test.
2. The final study should import Paper 4's schemas, estimators, metrics, and configuration variants, then add execution and deterministic result interpretation as separately versioned modules.
3. Paper 3-informed weights are a transfer condition and ablation, not ground truth.
4. Benchmarks using retrieval-derived “resolved” labels need citation-graph/full-text sensitivity analysis before conclusions about scientific resolution or neglect.
