# Full-text audit batch 55: uncertain dependencies, database repairs, and spatial co-location

Updated 2026-10-12. This closes the three lexical-priority records in the frozen `databases × 2015–2019` frame cell. They are distinct theory and systems tasks; no shared performance estimate is computed. Three sampled arXiv PDFs were retrieved and section-audited. Publication records and selected later primary sources were checked to separate settled subproblems from open ones.

## Sampled papers

### 1. On Desirable Semantics of Functional Dependencies over Databases with Incomplete Information (arXiv:1703.08198v2; Fundamenta Informaticae 2018)

[arXiv full text](https://arxiv.org/abs/1703.08198); [publication DOI](https://doi.org/10.3233/FI-2018-1651); local PDF: `data/fulltexts/arxiv/1703.08198v2.pdf` (24 pages); extracted text: `data/fulltexts/text/1703.08198v2.txt`.

The paper studies what a functional dependency (FD) should mean when a tuple can contain a set of possible values. It lists semantic desiderata (including Armstrong-style inference, independence from irrelevant attributes, and seamless satisfaction), proposes P-functional dependencies (PFDs) for the restricted “vague table” model, and proves that no FD semantics can satisfy the full listed package on the more expressive disjunctive-table model. Checking seamless satisfaction under weak FDs is NP-complete; PFD checking on vague tables can be supported with an index keyed by possible left-side valuations. This is a model/axiom trade-off, not an empirical claim about data cleaning accuracy. The authors explicitly say the desiderata are argued for intuitively and invite study of other/maximal property sets; the PFD result must not be generalized to every representation of incomplete information.

### 2. Computing Optimal Repairs for Functional Dependencies (arXiv:1712.07705v1; PODS 2018, expanded TODS 2020)

[arXiv full text](https://arxiv.org/abs/1712.07705); [PODS DOI](https://doi.org/10.1145/3196959.3196980); [expanded TODS version](https://doi.org/10.1145/3360904); local PDF: `data/fulltexts/arxiv/1712.07705v1.pdf` (34 pages); extracted text: `data/fulltexts/text/1712.07705v1.txt`.

The paper distinguishes two objectives that are often both casually called “repair”: an optimal subset repair (delete the least-cost tuples) and an optimal update repair (change the least-cost cells). For subset repairs it gives a dichotomy over sets of FDs: the algorithm succeeds in polynomial time on one side; otherwise the problem is APX-complete, even on unweighted, duplicate-free tables. This also resolves the general-FD most-probable-database dichotomy that had been open in the cited prior work. Update repairs do not inherit that complete classification: the paper gives sufficient conditions, hardness results, and constant-factor approximations, and proves examples where subset and update versions have opposite tractability outcomes. Its own Section 4 says a full U-repair dichotomy remains open.

Later work on *soft* FDs is adjacent, not the same objective: the 2024 TODS paper develops general hardness/approximation insights and algorithms for one FD and bipartite matching, but the general soft-FD problem remains only partially classified. Thus neither paper supports collapsing subset, cell-update, most-probable-world, and soft-constraint repair into a single complexity label.

### 3. Spatial Co-location Pattern Mining – A New Perspective Using Graph Database (arXiv:1810.09007v1; venue not independently verified)

[arXiv full text](https://arxiv.org/abs/1810.09007); local PDF: `data/fulltexts/arxiv/1810.09007v1.pdf` (8 pages); extracted text: `data/fulltexts/text/1810.09007v1.txt`.

The paper models spatial co-location patterns as cliques in a materialized neighborhood graph and presents three traversal algorithms with time/memory trade-offs. The evaluation is narrower than “large real-world data” might suggest: Chicago crime data reduced to 30,000 incidents across 33 primary crime types, stored in Titan with Cassandra plus MongoDB/Elastic components; the mining experiments use up to 30,000 graph vertices and a 48-thread pool. At 30,000 vertices and 0.3 km, the table reports 392 s for CliqueExtend, 578 s for CliqueEnumG, and 12,837 s for CliqueEnumK. When increasing the threshold from 0.4 to 0.5 km at 20,000 vertices, incremental graph update takes 111.4 s versus 313.8 s for a fresh graph construction (about 2.8× faster in that case, not orders of magnitude). CliqueExtend also needs more storage. These data support a regime-specific algorithm/memory trade-off, not a universal speedup over spatial databases or proof of real-time interactivity.

A 2024 publisher-hosted paper, “Graph-based spatial co-location pattern mining: integrate geospatial analysis and logical reasoning,” is a later graph-based approach, but its abstract describes a different adaptive-neighborhood/logical-reasoning method. It is not a controlled replication of the 2018 Titan/CliqueEnum algorithms; no common workload or direct performance comparison was identified in this targeted check.

## Bounded findings

1. **Incomplete-data FD semantics have a formal expressivity boundary, but “desirable” is still a chosen axiom set.** The sampled paper proves an impossibility for its joint desiderata on disjunctive tables while giving PFDs for vague tables. A theoretical follow-up can characterize maximal tractable representation/axiom pairs and make the cost of each relaxed property explicit. This lead weakens if an existing semantics already matches the same model, property list, and computational bounds; the current sample does not establish that none exists.

2. **Database-repair complexity depends on the repair operation, not just on the FD set.** The complete subset-repair dichotomy and general-FD most-probable-database resolution are positive evidence; counterevidence to broad closure is that cell-update repairs can be APX-hard for FD sets whose subset repairs are polynomial, and vice versa. The exact remaining theory target is a full update-repair dichotomy (and, separately, stronger classifications for soft FDs). A candidate classification is falsifiable by proving an FD-set is assigned to the wrong side or by finding a counterexample to a proposed criterion. No new classification was proved in this audit.

3. **Graph materialization speeds selected spatial-co-location workloads, but the evidence is small, old, and trade-off-sensitive.** The 2018 result compares three algorithms on one 30K-incident/33-type Chicago dataset and reports substantial runtime differences among its own methods; graph-threshold updates are faster than rebuilding but still take over 100 s in the cited case, and the fastest method pays in storage. A reproducible follow-up should compare spatial joins, graph traversal, and modern spatial/graph DBs on the same released datasets while varying event count, feature skew, neighborhood threshold, memory, and update rate. It weakens if graph materialization does not improve total build-plus-query cost or if query results change under equivalent spatial definitions. The 2024 graph paper is a neighboring method, not independent validation of this benchmark.

## Scope and limitations

These are three lexical-priority records from one frozen cell, not a representative estimate of all database theory or systems research. Later-source checks were targeted: the soft-FD publication abstract/record and 2024 spatial paper were used to assess follow-up status, not audited as full-text replications. No complexity theorem was re-proved, graph benchmark rerun, or code artifact examined. The results are bounded research leads, not novelty or prevalence claims across the 198,690-candidate corpus.
