# Full-text audit batch 40: software testing claims need an oracle-cost lens

Updated 2026-10-12. This batch reviews the seven previously unread uniform-random records in the `software_testing` topic-period cells. All seven were checked against full text. They range from unvalidated lifecycle/process proposals to empirical search-engine regression testing, LLM Android bug-oracle evaluation, and a quantum-software mapping study. The direct LLM test-oracle result is encouraging on known bugs but comes with a large false-alarm rate; counting detected candidates alone overstates operational value.

## Seven sampled records

### 1. Novel Integrated Approach of Software Development and Design Pattern with X-CM (arXiv:1401.8120v1; 2014)

[Full text](https://arxiv.org/pdf/1401.8120).

X-CM proposes a staged, hierarchical lifecycle for splitting and later integrating subprojects. The paper says it was tested with unit and integration tests and claims superiority to Spiral, Prototype, and V-Model, but the full text does not provide a controlled, quantitative comparative study of project outcomes, effort, or defect rates. Treat the claimed advantage as a proposal's claim, not measured comparative evidence.

### 2. From abstract modelling to remote cyber-physical integration/interoperability testing (arXiv:1403.1005v2; 2014)

[Full text](https://arxiv.org/pdf/1403.1005).

This paper presents a vision and modeling methodology for virtual/remote integration testing of geographically distributed cyber-physical systems. It emphasizes that abstraction assumptions must remain visible when moving from logical models to physical integration, and identifies unresolved questions about how to simulate robot interactions and environment constraints. The conclusion frames practical methodology as future work; it is not a controlled outcome study showing remote testing reduces costs or failures.

### 3. Reliability Testing Strategy – Reliability in Software Engineering (arXiv:1605.01097v1; 2016)

[Full text](https://arxiv.org/pdf/1605.01097).

This instructional report explains operational profiles, failure intensity, and test planning through a hypothetical pacemaker-system example. It walks through occurrence-rate assumptions and suggested scenario/load/performance/functional/stress/regression tests; it does not report a deployed medical system, prospective failure prediction, or measured reliability improvement. The illustrative rates are assumptions for an example, not observed field frequencies.

### 4. Academic Search Engines: Constraints, Bugs, and Recommendations (arXiv:2211.00361v1; 2022)

[Full text](https://arxiv.org/html/2211.00361).

The authors re-ran search interactions drawn from 621 software-engineering secondary studies across 42 digital libraries/indexers and documented 13 bugs in eight engines. The reproducible cases include query syntax, parentheses, field handling, and inconsistent results. But the study deliberately measures functional task completion/effectiveness, not usability with a broad user sample; interactions were reattempted by the paper's authors, and observations are snapshots from 2022. This is meaningful empirical evidence of search-tool fragility, not a timeless ranking of current engines.

### 5. A Study of Using Multimodal LLMs for Non-Crash Functional Bug Detection in Android Apps (arXiv:2407.19053v1; 2024)

[Full text](https://arxiv.org/html/2407.19053).

This is the most direct LLM-testing result in the sample. The study manually retained 71 reproducible non-crash Android bugs and compared GPT-4o-based test-oracle prompts with existing methods. Under its default integrated prompt, correct bug-and-description detection (TPC) is 49%, while false alarms on bug-free sequences are 59%. A lower-false-alarm single-prompt setting has 42% TPC and 29% FP; a repeated-query/integrated setting reaches 63% TPC but 93% FP. On a separate set of 64 apps the system surfaced 24 previously unrecognized bug candidates, of which four were confirmed or fixed. This is a real signal, but the tradeoff is operationally central: the high-recall settings can swamp reviewers, and 24 candidates are not 24 confirmed bugs.

### 6. Toward a Brazilian Research Agenda in Quantum Software Engineering: A Systematic Mapping Study (arXiv:2506.11013v2; 2025)

[Full text](https://arxiv.org/pdf/2506.11013).

The authors search 3,219 records and analyze 167 studies to map quantum software engineering and propose a Brazilian research agenda. Their mapping reports that conceptual/technical proposals predominate and empirical validation is limited. The result is a useful descriptive map, but its agenda is geographically framed; the general “field is immature” statement is not itself a measured intervention effect.

### 7. Protocol-Driven Development: Governing Generated Software Through Invariants and Continuous Evidence (arXiv:2605.12981v3; 2026)

[Full text](https://arxiv.org/html/2605.12981).

Protocol-Driven Development proposes structural, behavioral, and operational invariants plus validation evidence and runtime monitoring as a governance model for generated software. It gives illustrative handler, ETL, and microservice examples and an empirical evaluation agenda. Those examples are designs, not a controlled comparison demonstrating fewer defects, lower review cost, or better safety. The paper also explicitly leaves protocol authoring/inference and validation efficacy as open empirical issues.

## Bounded synthesis and falsifiable follow-up

This sample does not justify “LLMs are good test oracles” without specifying the cost of false alarms. In the Android study, the default setting finds about half of known bugs and also flags a majority of bug-free sequences; pushing recall higher raises the false-positive rate further. The independent search-engine study reinforces that test evidence must be reproducible and tied to observed task outcomes, while the X-CM, remote CPS, and PDD papers illustrate that a detailed testing/governance framework is not equivalent to evidence that it improves practice.

**Falsifiable follow-up:** On multiple app families and independently curated bugs, compare text-only, screenshot-only, and combined LLM oracles against conventional oracles using identical replayable test sequences. Blindly adjudicate all alerts. Report precision/recall, confirmed bugs per engineer-hour, reproducibility over repeated runs, and severity-weighted outcomes. The candidate that multimodal LLM oracles add practical value is weakened if their incremental confirmed-bug yield does not offset false-alarm triage time, or if the gains disappear on apps/bugs held out from prompt construction.

## Audit boundary

Seven papers close one random topic-cell set; they do not represent all software-testing literature. The Android study's benchmark was manually reduced from 399 candidate bugs to 71 reproducible cases, and its “new” results include only four confirmed/fixed reports. The search-engine study describes 2022 interfaces. Neither should be generalized beyond its setup without replication.
