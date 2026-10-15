# Full-text audit batch 39: “AI-generated code” is not one research area

Updated 2026-10-12. This batch closes the eight previously unread uniform-random records in the `ai_generated_code` topic-period cells. All eight were checked against their arXiv full texts (PDFs when HTML was unavailable). The label spans deterministic code transformation, runtime component composition, scientific DSLs, formal specification, formal foundations for physical simulators, one empirical LLM program-repair study, an LLM reverse-engineering proposal, and an agentic-software-engineering roadmap. Only one paper directly tests an LLM code-repair method, so results must not be pooled as if these were replications.

## Eight sampled records

### 1. Loo.py: transformation-based code generation for GPUs and CPUs (arXiv:1405.7470v1; 2014)

[Full text](https://arxiv.org/pdf/1405.7470).

Loo.py is a Python-embedded array-kernel system where programmers specify transformations such as tiling, vectorization, layout changes, and prefetching to generate OpenCL code. Its performance table measures kernels on three period-specific devices; this is compiler/tooling research, not learned code generation. The paper explicitly says correctness tests were more complete than performance measurements, and that comprehensive performance measurements were future work. Do not read its benchmark table as a general code-generator ranking.

### 2. Dynamic Component Composition (arXiv:1409.0526v1; 2014)

[Full text](https://arxiv.org/pdf/1409.0526).

This JavaBeans-oriented paper proposes composing runtime objects into new instantiable component types without generating code. It is a component-model/design contribution, not automated source-code synthesis or an AI study. The paper develops its model and implementation, but does not supply a modern, controlled comparative performance or developer-outcome evaluation.

### 3. A Domain Specific Language for Performance Portable Molecular Dynamics Algorithms (arXiv:1704.03329v2; 2017)

[Full text](https://arxiv.org/pdf/1704.03329).

Scientists express molecular-dynamics kernels in a domain-specific language, and a compiler framework emits CPU/GPU/distributed-memory code. The paper evaluates performance and scalability against established MD packages for selected systems. The tested GPU scaling advantage narrows at larger node counts, and the generated framework supports a narrower set of functionality than full packages such as LAMMPS/DL_POLY. Useful scientific code-generation evidence, but domain-specific and not evidence about LLM-generated code.

### 4. Comparative Study of Eight Formal Specifications of the Message Authenticator Algorithm (arXiv:1803.10322v1; 2018)

[Full text](https://arxiv.org/pdf/1803.10322).

This is a comparison of formal descriptions of a cryptographic message-authentication algorithm, including distinctions between declarative specifications and versions that can actually be executed/compiled. The authors document executability constraints and errors in an external C implementation. The lesson relevant to code-generation claims is methodological: a formal specification, an executable model, generated code, and verified deployed code are distinct evidence levels. It is not a generative-AI experiment.

### 5. The Mathematical Foundations of Physical Systems Modeling Languages (arXiv:2008.05166v2; 2020)

[Full text](https://arxiv.org/pdf/2008.05166).

This 116-page formal-methods paper develops foundations for compiling physical-system languages with mode-dependent differential-algebraic equations. It analyzes why two Modelica tools can fail on a mode switch in an idealized clutch example and proposes multimode structural analysis. Its proofs and examples are bounded by stated mathematical assumptions; this is not an empirical study of LLM code correctness or broad simulator coverage.

### 6. Counterexample Guided Program Repair Using Zero-Shot Learning and MaxSAT-based Fault Localization (arXiv:2502.07786v1; 2024)

[Full text](https://arxiv.org/html/2502.07786).

This is the one direct empirical LLM program-repair paper in the random draw. It combines MaxSAT fault localization, hole-filled program sketches, six roughly 7B open models, and counterexample-guided feedback. On 1,431 compiling-but-semantically-incorrect student C programs, the best all-model portfolio repairs 1,190 (83.2%) with reference implementations available, versus 907 (63.4%) for the strongest listed all-model portfolio without them. But reference code can be copied and may produce larger edits; the paper explicitly measures this tradeoff. Repair rates also fall with cyclomatic complexity: the strongest reported configuration repairs 17.1% in the hardest quartile. This is promising within introductory assignments, not yet evidence of the same benefit on industrial repository bugs, other languages, or longer-lived regressions. Counterexample feedback is not uniformly helpful for every model/configuration.

### 7. Beyond C/C++: Probabilistic and LLM Methods for Next-Generation Software Reverse Engineering (arXiv:2506.03504v1; 2025)

[Full text](https://arxiv.org/html/2506.03504).

The paper is a research proposal about binaries produced by languages such as Rust, Go, and Mojo. It motivates combining probabilistic analysis and fine-tuned LLMs, but does not report an implemented method, benchmark, or measured result. Treat its gap statements as proposed motivation, not independent confirmation that the gap exists or has been solved.

### 8. Agentic Software Engineering: Foundational Pillars and a Research Roadmap (arXiv:2509.06216v3; 2025)

[Full text](https://arxiv.org/html/2509.06216).

This paper organizes prior agentic-SE work and proposes a conceptual framework, processes, workbenches, and a research roadmap. It includes discussion of existing benchmark and in-the-wild work, but the proposed framework itself is not validated as a controlled intervention. It cannot be counted as a measured improvement in code-agent task success.

## Bounded synthesis and follow-up

The random sample does **not** support a claim that LLMs broadly improve code generation: six of the eight papers do not study LLM-generated programs, one is a proposal, and one is a conceptual roadmap. The one direct repair experiment does provide a useful, bounded signal: localization-guided sketches plus iterative test feedback can repair many introductory C assignments, while repair success falls sharply as program complexity rises and access to a reference implementation increases both success and copying/larger-edit risks. This narrows the actionable question to generalization and trade-offs, not whether “AI-generated code works.”

**Falsifiable follow-up:** On both introductory assignment sets and real repository bug-fix tasks, hold model, test budget, and timeout fixed. Randomize ablations of fault localization, hole/sketch prompting, and counterexample feedback. Stratify by bug type and pre-repair complexity; score hidden-test correctness, regression rate, edit size, and human review effort. The candidate interaction is weakened if localization/sketch/feedback gains remain equally large across complexity and task domains, with no increase in edit size or regressions. Report per-model/configuration results rather than only the best-of-model portfolio.

## Audit boundary

This closes the eight sampled keys in one lexically defined topic cell; it is not an exhaustive review of code-generation literature or a prevalence estimate. The cell is visibly heterogeneous, and the single direct LLM repair experiment does not establish novelty. Industrial repository evaluation and independent replication remain necessary.
