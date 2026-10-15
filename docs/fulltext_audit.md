# Full-text spot audit of initial candidate papers

Reviewed 2026-10-11. This is a first-pass source audit for question candidates,
not a systematic review. The records link to the exact arXiv paper page; arXiv
API metadata gives the latest version available on the review date.

| Paper | Sections checked | Directly supported observation | Candidate question use |
|---|---|---|---|
| AMA-Bench, arXiv:2602.22769v4 | Introduction, empirical motivation, ablations | The authors report memory systems often underperforming a long-context baseline; their ablation separates information loss during memory construction from retrieval loss. | Motivates a matched-budget replication of memory representations and retrieval. |
| AgentLAB, arXiv:2602.16901v1 | Introduction, defense evaluation | The authors report 28 environments, 644 cases, and that one-turn defenses do not reliably mitigate long-horizon attacks. | Motivates controlled defense transfer under matched attack and interaction budgets. |
| SWE-bench, arXiv:2310.06770v3 | Introduction, discussion/limitations | The benchmark is drawn from real repository issues; the paper explicitly notes its tasks are Python-only and that execution-based tests alone do not guarantee quality, readability, or efficiency. | Motivates repository-held-out and broader-language evaluation. |
| OK-Robot, arXiv:2401.12202v2 | Section V, open problems | The authors explicitly identify static semantic/obstacle maps and multiplicative module failures, and propose dynamic maps plus failure detection/recovery as research directions. | Supports two concrete, separately testable robotics questions. |
| Testing Database Engines via Query Plan Guidance, arXiv:2312.17510v1 | Abstract and introduction | The authors describe QPG as targeting test diversity by query plans and report comparisons on SQLite, TiDB, and CockroachDB. | Motivates replication across engines and workloads. |
| How Often Do Single-Statement Bugs Occur? The ManySStuBs4J Dataset, arXiv:1905.13334v2 (MSR 2020) | §§2.1–2.7, 3–4, 6 | The dataset contains 153,652 mined single-statement changes from 1,000 Java projects; 33.47% of the large-version changes match at least one of 16 patterns. The authors warn that commit-message heuristics can introduce false positives, bugs are not severity-labeled, and the dataset is Java-only. | Candidate: do repair methods evaluated on template-matched Java one-line bugs generalize to non-template defects, larger changes, and other languages? The dataset supports prevalence within its mining frame, not prevalence across all software. |
| FairFuzz, arXiv:1709.07101v1 | Abstract, §4 evaluation, §5 discussion | Rare-branch-focused seed selection and input mutation improve coverage on some benchmarks; the authors report faster high coverage on others, but explicitly say results vary by benchmark. They did not evaluate the parallel laf-intel configuration and note the implementation lacked distributed rare-branch computation. | Candidate: under equal CPU-hours, how consistently do rare-branch-aware mutators improve bug discovery—not just coverage—across modern, diverse targets? |
| Comparing Fuzzers on a Level Playing Field with FuzzBench (ICST 2022) | Abstract; §III experimental design; §V results, especially fuzzer summary; §VII conclusions | Includes FairFuzz among nine fuzzers, 12 systems, 183 real-world bugs, and 30 repeated 23-hour campaigns per fuzzer/benchmark. FairFuzz ranks near the bottom for efficacy but is reported as the most efficient for additional crashes / time to last distinct crash; coverage–bug correlation varies more by system under test. | This creates a concrete outcome-metric tension with FairFuzz's coverage-focused results, not a simple replication failure: coverage, total bug efficacy, and time efficiency point in different directions. The refined question is whether rare-branch guidance improves confirmed unique-bug yield per equal CPU-hour across target classes, and whether its effect is mediated by target properties. |
| Look Before You Leap: An Exploratory Study of Uncertainty Analysis for LLMs, arXiv:2307.10236v4 | §§V-A–V-D, VI-A, VII | Across NLP and code tasks, uncertainty techniques have heterogeneous performance. In the code tables, AUC varies substantially by model and task; the authors state that uncertainty does not necessarily indicate correctness, subtle errors are hard to detect, and more tasks (including repair and translation) remain to be studied. | Candidate: when, and at what cost, does uncertainty provide useful risk ranking beyond task-specific behavioral tests for code generation, repair, and translation? |
| Assessing Correctness in LLM-Based Code Generation via Uncertainty Estimation, arXiv:2502.11620v3 | Abstract, §§1, 4–5.1, Appendix C | The authors report that embedding- and CodeBLEU-based semantic clustering did not yield significant correctness correlation, while symbolic-execution-based clustering did on LiveCodeBench; their equivalence checks are bounded/time-limited and their abstention thresholds use a train/validation procedure. | **Evidence tension with the previous study, not a settled contradiction:** estimates are weak or inconsistent for some proxies, but useful under symbolic clustering and this benchmark. A testable question is whether those gains survive larger repository-level tasks and bounded-verification failures. |
| Lessons from Studying Two-Hop Latent Reasoning, arXiv:2411.16353v4 | §§2–5, especially §5 Results; §6.1–6.2; Appendix F | The study reports near-zero no-CoT two-hop performance when both facts are synthetic, but above-chance performance in a semi-synthetic setup that connects newly taught facts to pretrained real-world knowledge. The authors say the large gap needs further investigation and describe the setup as a toy model with limitations. | Candidate: is apparent latent multi-hop reasoning caused by compositional capability, pretrained bridge-entity knowledge, or task construction? Match fact distributions and probe bridge knowledge to distinguish these explanations. |

These additions are HTML full-text checks of the listed arXiv versions, not
independent replications. Section names are the exact navigable locators in the
versioned source; arXiv HTML has no stable printed page numbers. For the LLM
uncertainty candidate, the two papers do not simply cancel each other: they
test different models, benchmarks, estimators, semantic-equivalence proxies,
and correctness criteria. The appropriate extraction is a conditional
question about method/task generalization, not the claim that either paper
settles whether “uncertainty works.”

The first-pass evidence does not establish that these are globally unresolved or
high-value questions. It establishes that the cited source supports the stated
problem context or identifies a gap. Each question still needs related-work
search, independent contradictory evidence, and a frozen experimental
operationalization before ranking.

An additional 18 source-located records are documented in
[`fulltext_audit_batch2.md`](fulltext_audit_batch2.md) and
`data/audited_research_questions_batch2.jsonl`. Together with the four records
in the first batch, the working inventory now contains 22 full-text-audited
question candidates. This remains a targeted sample, not an exhaustive review
of the 2,106-paper candidate pool or the full CS literature.
