# Full-text audit batch 25: database-labelled papers span very different evidence levels

Updated 2026-10-11. Read all six unread uniform-random records in the fixed `databases` topic-period cells for 2020–2024 and 2025–2026 through the cutoff (three per period). This is a sample from the declared arXiv retrieval frame, not a systematic review of database research. The database label is imperfect: it includes a broad TEE survey, a ChatGPT/semantic-schema case study, a blockchain privacy prototype, a text-to-SQL benchmark paper, a drift benchmark, and an agent-memory database prototype.

## 2020–2024 records

### 1. A Survey of Secure Computation Using Trusted Execution Environments (2023)

[Li et al., arXiv:2302.12150v1](https://arxiv.org/abs/2302.12150); [full arXiv HTML](https://arxiv.org/html/2302.12150), §§2–5 and Appendix A.

This is a survey/taxonomy, not a new database implementation. It separates outsourced, distributed, and multiparty computation, and compares protocols along setting, methodology, security goals/adversary models, and performance. Its database-query appendix says most hardware-backed encrypted database systems target SQL over relational databases, with some key-value/document-query systems, and very few studies address streaming data (the survey names Park et al. 2019 as an exception). The authors also catalogue TEE side channels, rewind/state attacks, trust assumptions, and the cost/limitations of crypto alternatives.

**Boundary:** the paper organizes a broad protocol literature and its reported comparisons inherit the different machines, datasets, threat models, and query tasks of the underlying studies. It is not a controlled head-to-head database benchmark. The “few streaming studies” observation is a survey finding, not a count independently reconstructed in this audit.

### 2. Context-based Ontology Modelling for Database: Enabling ChatGPT for Semantic Database Management (2023)

[Lin et al., arXiv:2303.07351v1](https://arxiv.org/abs/2303.07351); [full arXiv PDF](https://arxiv.org/pdf/2303.07351), §§3–5.

COM-DB expresses schema relations in natural language, including a “context-of” construct. The two case studies use two healthcare-style databases. In semantic integration, the baseline ChatGPT response misses mappings (e.g., Name/FIRST and Surname/LAST); with the contextual schema it returns the illustrated target mapping. In a second task, the no-context SQL omits the encounters table and fails execution; the context-augmented query executes to the intended view. The authors repeat each experiment ten times and describe average results.

**Counterweight and boundary:** this supports schema context as a plausible aid on the two illustrated tasks, not broad text-to-SQL improvement. The paper itself says it needs larger databases and more complex operations; it does not establish accuracy across a broad benchmark, model families, schemas, or independently authored tasks. The evidence is case-study scale, despite the repetitions.

### 3. Privacy-Preserving Data Management using Blockchains (2024)

[Kwakye, arXiv:2408.11263v1](https://arxiv.org/abs/2408.11263); [full arXiv HTML](https://arxiv.org/html/2408.11263), §§III–V and Table II.

The system couples relational data and privacy preferences with a permissioned blockchain used for authorization/audit. On one machine (8 logical processors, 16 GB RAM), it compares privacy-aware and native queries for three data categories. For the demographic query class it reports mean latency 22.99 ms versus 13.37 ms (41.85% overhead); for healthcare data, 21.67 ms versus 13.38 ms (38.26% overhead). These are useful measured costs rather than a cost-free “privacy” claim.

**Boundary and counterweight:** the evaluation is a single-machine implementation with selected query classes; it does not establish multi-node throughput, production-scale behavior, or resistance to a broad set of implementation/side-channel attacks. The paper explicitly says its unique privacy models, infrastructures, and blockchain platforms make direct performance comparison with other systems impractical. Therefore the latency result is local to its test setup, and the security claim should be read against its stated adversary model.

## 2025–2026-through-cutoff records

### 4. The Interpretability Analysis of the Model Can Bring Improvements to the Text-to-SQL Task (2025)

[Zhang, arXiv:2508.13178v1](https://arxiv.org/abs/2508.13178); [full arXiv PDF](https://arxiv.org/pdf/2508.13178), §§3–5 and Tables 1–3.

CESQL combines LIME-based token analysis, execution guidance, filtering/correlation rules, and model fusion for WikiSQL. Table 1 reports test logical-form accuracy 87.7% and execution accuracy 93.0%, versus 87.1%/92.7% for the listed SeaD+EG comparator. In the rule-based aggregation setting (Table 2), CESQL reports 88.0%/93.1%, while SeaD+EG_ACS reports 87.5%/93.0%; however IESQL+EG+AE has higher logical-form accuracy (87.8% versus 87.7%) and lower execution accuracy (92.5% versus 93.1%). Results are thus small, metric-dependent advantages, not a uniform win.

**Boundary:** the paper explicitly focuses on WikiSQL's single-table/basic-query setting and frames complex queries and irregular real-world data as future work. It also says interpretability adds noticeable processing time. The evidence does not show transfer to current multi-table text-to-SQL benchmarks or that LIME explanations are faithful causal explanations of the model.

### 5. DriftBench: Defining and Generating Data and Query Workload Drift for Benchmarking (2025)

[Liu and Borovica-Gajic, arXiv:2510.10858v1](https://arxiv.org/abs/2510.10858); [full arXiv HTML](https://arxiv.org/html/2510.10858), §§2–5.

DriftBench defines data changes (cardinality, row updates, distribution skew, outliers), workload changes (predicate distributions/selectivity and query structure/payload), and temporal arrival patterns. Its demonstrated implementation supports CSV/PostgreSQL. In its cardinality-estimation case study, it uses the census dataset, two drifted data variants, and six workloads, comparing PostgreSQL, Naru, and MSCN by Q-error behavior. The observed pattern is estimator-specific: PostgreSQL's average Q-error is fairly stable but outlier spread/count shifts; Naru changes substantially on skewed census-drift2; MSCN responds to both data and workload shifts.

**Counterweight and boundary:** this provides a useful controlled benchmark-generation tool and shows that drift can change which estimator looks robust. It does not yet establish that its generated drifts match production database evolution, nor does the paper evaluate indexing/caching/query-planning impacts (named as future extensions). The cardinality-estimation case study is on one census dataset; it emphasizes response patterns rather than a broad absolute-accuracy leaderboard.

**Prior-work check:** the 2021 DSB paper is a direct counterexample to any broad claim that dynamic database benchmarks did not exist before DriftBench. DSB extends TPC-DS with more complex distributions and query templates, configurable/dynamic workloads, and reports evaluation methodology; its code and artifacts are public. DriftBench therefore should be framed more narrowly: a schema-driven generator for composable data, query, and temporal drift, demonstrated jointly for cardinality estimation—not the first dynamic-workload benchmark. DSB's focus is also narrower in another direction (TPC-DS-based decision-support schemas), so the two tools may be complementary rather than redundant.

### 6. MemoriesDB: A Temporal-Semantic-Relational Database for Long-Term Agent Memory (2025)

[Ward, arXiv:2511.06179v1](https://arxiv.org/abs/2511.06179); [full arXiv HTML](https://arxiv.org/html/2511.06179), §§3–5.

MemoriesDB combines append-only temporal records, vector embeddings, and labeled graph relations in PostgreSQL/pgvector. The full text is unusually explicit about evidence status: its table of insert latencies/throughputs is called “illustrative estimates” and “not results from formal benchmarking”; later it says the prototype is meant to demonstrate feasibility rather than compete with optimized engines, reports no formal coherence metrics, and says agent-behavior validation is still warranted. Its limitations include stationary-embedding assumptions, deletion/privacy complications, and query costs that rise with vector dimensionality.

**Boundary:** the architectural proposal and executable prototype can motivate experiments, but the reported scale/performance numbers cannot be treated as measured benchmark results. The paper's statements about coherent recall or cognitive benefits remain hypotheses until tested against matched memory baselines on real agent tasks.

## Bounded cross-paper result and next experiment

In this six-item slice, “database progress” spans a protocol survey, schema-context case study, local privacy-aware query prototype, single-table text-to-SQL benchmark, generated-drift benchmark, and agent-memory architecture. Their outputs cannot form a single trend. A more useful cross-paper question is whether a database system's claim is backed by the evidence level it implies: theorem/taxonomy, task demonstration, measured single-host prototype, controlled benchmark, or externally validated workload.

**Falsifiable follow-up:** pre-register a database-evidence card for each system: data/schema/workload provenance; number and diversity of databases and query templates; threat model when privacy/security is claimed; tuned baselines; independent repeated runs; measured latency/throughput/resource overhead; and whether the workload is external/held out. For drift tools, compare DSB and DriftBench on common TPC-DS-style and non-TPC schemas, separately and jointly varying data, workload, and arrival-time drift. Measure generator validity, estimator ranking stability, and downstream plan/runtime effects. The hypothesis that composable drift generation adds transferable coverage is weakened if DriftBench scenarios are unrealistic, fail to port, or reveal no additional failure modes beyond DSB. More broadly, re-run selected privacy-aware query, text-to-SQL, drift, and agent-memory systems on shared, version-pinned workloads. The evaluation-maturity hypothesis is weakened if claimed gains persist across held-out databases/workload shifts, matched systems, threat models, and repeated independent runs.

This is six full-text checks from two random-frame cells, not an estimate of how common any evidence level is in the database field, and not an exhaustive search or novelty claim.
