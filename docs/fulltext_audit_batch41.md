# Full-text audit batch 41: relevant code is not always good code

Updated 2026-10-12. This batch closes the seven previously unread uniform-random records in `compilers_programming_languages`, then adds one independent full-text citation follow-up (CodeRAG-Bench). The sample spans web-language benchmarking, a language for infinite structures, an industrial coding standard, sparse-tensor compilation, blockchain workflow execution, an LLM programming framework, and quality-aware code retrieval. The cross-paper signal is specifically about measurement: conventional retrieval relevance can miss code quality on some tasks, while useful/high-quality context can improve generation when it is actually retrieved and used. Neither source supports the slogan that relevance is always useless or that RAG automatically improves software.

## Seven sampled records

### 1. Process-aware web programming with Jolie (arXiv:1410.3712v3; 2014)

[Full text](https://arxiv.org/pdf/1410.3712).

Jolie extends a process-oriented language for web servers, stateful processes, service composition, and client/server validation. The paper does include performance tests: static and templated pages are compared with Apache/PHP and GlassFish/JSP and show roughly comparable throughput in the tested setup. A service-aggregation experiment uses 20–80 upstream services and 250–1,000 clients; throughput degrades as services grow, but less than linearly because calls are parallelized. These are useful measured outcomes, but the authors explicitly call them representative experiments on one i5-2500K/8GB server, not a production-scale framework ranking.

### 2. SMT Solving for Functional Programming over Infinite Structures (arXiv:1604.01185v1; 2016)

[Full text](https://arxiv.org/pdf/1604.01185).

Nλ is a Haskell-embedded language for finite representations of first-order-definable infinite structures, using an SMT solver to answer set and formula questions. The paper demonstrates transitive closure and graph k-colorability. Its own discussion distinguishes the examples: finite transitive-closure code transfers nearly verbatim, while infinite-graph coloring needs domain-specific mathematics and a different equivariant construction. This is a language/proof-of-concept contribution, not a broad benchmark of runtime or programmer productivity.

### 3. The MISRA C Coding Standard and its Role in the Development and Analysis of Safety- and Security-Critical Embedded Software (arXiv:1809.00821v1; 2018)

[Full text](https://arxiv.org/html/1809.00821).

This is a technical overview of MISRA C and its relationship to static analysis and formal methods, not a controlled measurement of its effect on defect or incident rates. It makes an important distinction for automated checking: some rules are decidable from source, while others require approximations; a checker that says “yes” for uncertain cases risks false positives, while suppressing “unknown” can miss violations. MISRA is designed for a documented process that records justified deviations, rather than an automatic pass/fail proof of safety.

### 4. CoNST: Code Generator for Sparse Tensor Networks (arXiv:2401.04836v1; 2024)

[Full text](https://arxiv.org/html/2401.04836).

CoNST uses a constraint model to choose contraction order, loop fusion, and sparse layout jointly, then lowers the result through TACO to executable code. In selected quantum-chemistry and sparse-tensor workloads it reports large gains over TACO, SparseLNR, and Sparta; one three-index integral case is about two orders of magnitude faster than the compared alternatives. But the comparison is workload-specific: one larger four-index experiment could not run due to platform memory limits, and some baseline configurations also ran out of memory. This is strong evidence for the tested sparse contractions, not a general compiler speedup claim.

### 5. The Cost of Executing Business Processes on Next-Generation Blockchains: The Case of Algorand (arXiv:2407.06725v1; 2024)

[Full text](https://arxiv.org/pdf/2407.06725).

The authors formalize Algorand transaction/storage costs and compile BPMN choreographies into TEAL contracts, testing supply-chain and incident-management process cases in a local Algorand sandbox. A key result is that minimum-balance requirements can dominate the apparent transaction-fee comparison: participant balances make up as much as 85% of total cost in the studied case. The authors also bound their evidence: AVM cost results use static local runs, omit some shared external-account balance costs in headline comparisons, and do not model changing congestion. “Cheap blockchain execution” is therefore workload-, price-, and cost-accounting-dependent.

### 6. Oracular Programming: A Modular Foundation for Building LLM-Enabled Software (arXiv:2502.05310v5; 2025)

[Full text](https://arxiv.org/html/2502.05310).

Oracular programming separates explicit search/strategy code from LLM calls and treats demonstrations as typed, testable program components. Unlike a pure vision paper, it includes a matched-budget Code2Inv experiment: with the same demonstrations/advice and a 20-cent-per-problem cap, its abduction-based GPT-4o-mini system solves all 124 benchmark problems at a reported average 0.12 cents each, while ReAct baselines solve 113–124 with higher average cost. Results average three random seeds. This is a concrete positive signal for one invariant-synthesis workload and orchestration, not evidence that the programming abstraction improves arbitrary coding-agent tasks; the paper notes conceptual/physical overhead and presents only a handful of case studies.

### 7. CoQuIR: A Comprehensive Benchmark for Code Quality-Aware Information Retrieval (arXiv:2506.11066v3; 2025 arXiv version; ACL 2026)

[Full text](https://arxiv.org/html/2506.11066) · [ACL 2026 version](https://aclanthology.org/2026.acl-long.512/).

CoQuIR annotates correctness, efficiency, security, and maintainability across 42,725 queries and 134,907 snippets in 11 languages; it evaluates 23 retrievers on seven datasets. This is the clearest signal in the random draw: high semantic/relevance scores often fail to imply high code quality, especially for security and maintainability tasks. The authors also report important counterevidence: relevance and quality metrics correlate strongly on CodeNet-B and CVEFixes, but poorly on SafeCoder and DepreAPI. Thus relevance is an unreliable **general** proxy, not a useless metric. Quality-aware fine-tuning improves retrieval scores and selected downstream generation/security outcomes. Limitations include some LLM-generated query summaries and no extensive comparison with static filtering or unit-test-based pre/post-retrieval controls.

## Independent full-text follow-up: CodeRAG-Bench

[Full text, NAACL Findings 2025](https://aclanthology.org/2025.findings-naacl.176.pdf).

CodeRAG-Bench evaluates 10 retrievers and 10 generation models over basic, open-domain, retrieval, and repository-level coding tasks, with a 25-million-document datastore and executable end-to-end evaluation. It provides counterweight to any claim that retrieval itself is harmful: canonical/high-quality documents improve code generation in multiple settings (the paper reports a 27.4% gain for GPT-4o on SWE-Bench and 6.9% on a harder ODEX subset). At the same time, open retrieval often fails to find useful evidence, the generator may not exploit it, and gains on repository-level tasks are limited. It is not a direct replication of CoQuIR: CodeRAG-Bench focuses on Python and code-generation outcomes, while CoQuIR isolates retrieval quality over more languages and quality dimensions.

## Bounded synthesis and falsifiable follow-up

Together these two independent studies sharpen the research question: **does ranking code by correctness/security/efficiency/maintainability add downstream value beyond ranking by semantic relevance, and under which task conditions?** CoQuIR says the two rankings diverge in some of its seven retrieval tasks, but not all; CodeRAG-Bench shows that genuinely good supporting context can improve executable code, while ordinary retrievers and generators often fail to make that potential real. Therefore “more relevant context helps” and “retrieval is broken” are both too broad.

**Falsifiable follow-up:** Use held-out repositories and multiple languages. Compare no retrieval, relevance-only top-k, quality-aware reranking, and oracle high-quality evidence under fixed context/token budgets. Evaluate exact retrieval preference plus end-to-end compilation/hidden tests, static security checks, efficiency, and maintainability review. Deduplicate repositories and freeze model training cutoffs to limit contamination. The added-value claim is weakened if quality-aware ranking does not improve these downstream outcomes over relevance-only ranking on held-out tasks, or if it improves offline preference metrics without improving generated-code quality.

## Audit boundary

This closes one seven-paper random topic-cell set. CodeRAG-Bench is a deliberate citation follow-up, not part of the random sample and not an independent replication of CoQuIR. Both benchmarks have task/language/model limitations; the candidate is a research-design lead, not a novelty claim or a pooled effect estimate.
