# Full-text audit batch 71: compilers/programming languages, 2020–2024

This closes the six-record `compilers_programming_languages × 2020–2024` sample cell: three lexical-priority papers audited here and three uniform-random papers reconciled to their earlier full-text audits. The papers study different things (multilingual code-generation benchmarks, Java vulnerability prediction, learned code representations, formal protocol safety, sparse-tensor compilation, and blockchain workflow cost); their metrics are not pooled.

## Three new full-text audits

### MultiPL-E: A Scalable and Extensible Approach to Benchmarking Neural Code Generation (`2208.08227v4`)

MultiPL-E translates HumanEval and MBPP from Python to 18 additional languages, then evaluates Codex, CodeGen, and InCoder primarily with unit-test pass@1. The benchmark is carefully engineered: MBPP assertions are removed from prompts and used as hidden tests; target-language signatures and tests are compiled or adapted. The authors explicitly warn that the resulting prompts/tasks are not representative of real programming in every language. Some HumanEval problems are excluded or altered for compilation/type-system incompatibility (up to five in some typed-language settings), and small prompt choices can materially change scores (e.g. argument naming or comment style).

**Boundary:** the measured quantity is success on a translated, small, interview-style benchmark under a particular translation and prompt protocol—not general cross-language software-engineering competence. The paper’s own analysis finds language frequency and features associated with outcomes and demonstrates prompt sensitivity. This is a strong, extensible benchmark contribution; the boundary motivates testing robustness of cross-language rankings to test strength and translation choices, rather than dismissing its results.

### Explaining the Contributing Factors for Vulnerability Detection in Machine Learning (`2406.03577v1`)

Across 17 real Java projects (including 15 Android applications), the study compares tokenization, bag-of-words/word2vec/fastText features, eight architectural metrics, and random forest/SVM/ResNet classifiers. It reports bag-of-words plus random forest as a useful baseline, about four percentage points more accurate than the other tested combinations. The paper then directly evaluates transfer: train on one Android project and predict others; at an 0.8 precision-and-recall threshold it averages 1.4 projects, and training on 14 projects then testing on the held-out fifteenth reaches the threshold on 5/15 projects. The paper also reports 10/15 above the 0.7 threshold.

**Boundary and counterevidence:** this is positive evidence for a simple baseline within its Java/project data and explicit evidence that cross-project transfer is uneven—not evidence that transfer is unstudied. The authors note a limited number of projects, that Android Study vulnerability labels inherit static-analysis labels that may include false positives, and that only Java was used. The same-project factor comparisons use within-project train/test splits; the paper’s strongest transfer results require pooling projects from the same Android domain. Independent cross-project/domain-adaptation work predates this paper, so transferability alone is not a novelty claim.

### DeepCodeProbe: Towards Understanding What Models Trained on Code Learn (`2407.08890v1`)

DeepCodeProbe probes AST-derived representations in four non-transformer software-maintenance models across clone detection, summarization, and comment generation. Its results support that these relatively small models encode some abstract syntactic structure; increasing capacity can improve syntax probe performance but also brings training/overfitting trade-offs. The paper uses validation checks (including clone/non-clone similarity and trained versus randomly initialized models) and provides a replication package.

**Boundary:** the paper explicitly identifies probe construct validity as a threat: a trained probe can distort what a representation means. Its models are older non-transformer architectures chosen because code/data were available for replication, and its outcome is primarily recoverable syntactic information—not whether a probe score predicts functional correctness, security, or reliability on future maintenance tasks. Earlier AST-probing and later syntax/semantics studies are counterevidence to any claim that code-model syntax probing itself is unexplored.

## Uniform-random sample already audited (reconciled, not re-read as new evidence)

- **Multiparty Session Types for Safe Runtime Adaptation in an Actor Language** (`2105.06973v1`; batch 20): formal protocol-safety/progress properties plus an adaptive DNS feasibility example. It does not measure production throughput or reliability; protocol compliance does not prove the discovered service is honest or semantically correct.
- **CoNST: Code Generator for Sparse Tensor Networks** (`2401.04836v1`; batch 41): strong results for selected sparse-tensor contractions/layouts, including a very large speedup in one case; some larger workloads exceed platform memory. Not a general compiler speedup estimate.
- **The Cost of Executing Business Processes on Next-Generation Blockchains: The Case of Algorand** (`2407.06725v1`; batch 41): compiler and cost comparison on two local workflow examples. Minimum-balance charges can dominate costs; static local runs do not model network congestion, and cost claims depend on historical exchange rates and accounting assumptions.

## Findings and next tests

The most actionable bounded lead is **benchmark-configuration sensitivity in multilingual code generation**. MultiPL-E itself demonstrates prompt/translation sensitivity, while EvalPlus shows that substantially expanding HumanEval tests can catch wrong solutions and even reverse model rankings in the Python benchmark. This is not evidence that MultiPL-E’s language rankings are wrong; it motivates a direct, paired test: strengthen translated test suites, vary reasonable prompt/translation choices, and measure per-language pass rates and rank stability. If rankings and conclusions persist across these perturbations, the concern weakens. LiveCodeBench supplies complementary evidence that benchmark freshness/contamination and task scope matter, but it is not a direct multilingual replication.

A second question is whether **probe-measured syntax knowledge predicts downstream correctness or maintenance success** in current transformer/code LMs. The sampled DeepCodeProbe paper addresses older non-transformers and recognizes probe validity limits; earlier/later syntax-probing papers provide counterevidence that syntactic structure can be recovered from model states. A useful study must therefore compare probe scores with held-out executable correctness/security/maintenance outcomes, under controls for model size, task, language, and probe capacity. This is a research lead, not a verified gap or novelty claim.

The vulnerability paper contributes an informative baseline and uneven transfer measurements, but cross-project vulnerability transfer has already been studied (including domain-adaptation and cross-language transfer papers). The next step there is not “does transfer exist?”; it would need a carefully deduplicated, leakage-resistant benchmark and consistent threshold/calibration reporting across project and language shifts.

## Sources

- https://arxiv.org/abs/2208.08227v4
- https://arxiv.org/abs/2406.03577v1
- https://arxiv.org/abs/2407.08890v1
- https://arxiv.org/abs/2105.06973v1
- https://arxiv.org/abs/2401.04836v1
- https://arxiv.org/abs/2407.06725v1
- Follow-up primary papers: https://arxiv.org/abs/2305.01210 (EvalPlus), https://arxiv.org/abs/2403.07974 (LiveCodeBench), https://arxiv.org/abs/2206.11719 (AST-Probe), https://arxiv.org/abs/2212.10017 (syntax/semantics probing), and https://arxiv.org/abs/2209.10406 (cross-project vulnerability domain adaptation).

This is one completed six-record cell in a fixed retrieval-prioritized sample. It is not a systematic review, prevalence estimate, independent reproduction, or global novelty determination.
