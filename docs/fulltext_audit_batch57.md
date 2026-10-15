# Full-text audit batch 57 — software testing, lexical-priority 2015–2019

This batch closes the two remaining lexical-priority records in the frozen `software_testing × 2015–2019` cell. The period is arXiv first-submission period, not necessarily the publication year. Both arXiv PDFs were downloaded and text-extracted locally; IDs, topic, period, and sampling arm match `data/fulltext_stratified_sample.jsonl`.

## 1. Fuzzy Adaptive Tuning of a Particle Swarm Optimization Algorithm for Variable-Strength Combinatorial Test Suite Generation (`1810.05824v1`)

This paper presents FPSO, a particle-swarm method that uses Mamdani fuzzy rules to adjust inertia during variable-strength combinatorial test-suite generation. It compares suite sizes with PSTG, CPSO, and DPSO on three variable-strength covering-array configurations. Each experiment is run 30 times; both best and mean suite size are reported. The authors explicitly exclude execution-time comparison because implementations and environments differ.

The results do not show FPSO as the general winner. DPSO has the best overall minimum size; it also has the lowest mean in 8/12 and 5/7 entries in two tables. FPSO obtains the lowest mean in 3/7 entries in the third table, while the paper's 95% interval-plot discussion still describes DPSO as having the lowest overall mean distribution and FPSO as runner-up. The authors call FPSO feasible and comparatively lightweight, but state that further empirical evaluation is warranted and that a best result may occur by chance in a stochastic run.

The measured outcome is generated test-suite size, not execution on a software-under-test, fault detection, runtime, or engineering cost. Consequently, this experiment supports a conditional claim about suite-size results on its chosen configurations; it does not establish greater fault-finding effectiveness. Venue metadata was independently checked against the UMPSA institutional repository: an IET book chapter in *Swarm Intelligence, Volume 3: Applications* (2018), pp. 1–21 in that repository's record. The arXiv PDF itself labels the manuscript a preprint submitted to an IET book chapter.

## 2. Empirical Notes on the Interaction Between Continuous Kernel Fuzzing and Development (`1909.02441v1`)

This six-page exploratory study analyzes a snapshot of syzbot reports collected on 30 June 2019 across Linux, FreeBSD, NetBSD, and OpenBSD. It reports more than 800 unresolved crash reports. For pending reports, median days-since-reported are 136 (Linux), 51 (FreeBSD), 53 (NetBSD), and 119 (OpenBSD); for closed Linux reports, median time-to-fix is 38 days. The paper reports that roughly 23% of fixed Linux-kernel bugs had a reviewed-by and/or tested-by marker in commit messages, and that code-churn measures provide only a weak signal for fix time.

Important limits are explicit in the paper: a crash report need not be a unique bug; false positives and non-reproducibility are known issues; the dataset is one early snapshot; review/test labels are inferred from commit-message strings; Linux and BSD data are not fully comparable; and the authors call for comparison with conventionally found bugs. Thus backlog size is not a count of distinct confirmed defects, and report-to-fix time does not isolate the time before a bug becomes reachable to a fuzzer.

Venue verified from primary author and proceedings records: IEEE ISSREW 2019, pp. 276–281, DOI 10.1109/ISSREW.2019.00084.

## Targeted full-text follow-ups and counterevidence

### Combinatorial test-suite metrics and fault detection (`2610.02560v1`)

The arXiv v1 full PDF was checked as a targeted, post-sample follow-up (submitted 2026-10-01, within the corpus cutoff). It reports correlations between static test-suite metrics and fault-detection effectiveness, using eight open-source programs in the abstract and 295,624 test suites; its body instead refers to nine programs and 36 scenarios. It reports VCC as the best overall predictor in its experiments and notes that VCC at strength 1 can saturate too early. Its fault set mixes verified mutation faults for five SIR programs with previously reported, developer-confirmed real faults for BusyBox, Drupal, and Linux Kernel; metrics correlate with fault counts in those scenarios, not with field production rates.

This is substantive counterevidence to any broad statement that static combinatorial metrics have not been compared to fault detection. It does not validate FPSO itself, since the 2018 FPSO experiment did not run the generated suites against faults. Caution is essential: the 2026 paper is an arXiv v1, and its front matter includes unresolved JACM/2018/DOI placeholder metadata while the arXiv submission is dated 2026; the abstract and methods also disagree on subject/scenario counts. Treat its result as an important, unreviewed evidence lead requiring source-data and artifact verification, not as settled replication evidence.

### SyzRetrospector: A Large-Scale Retrospective Study of Syzbot (`2401.11642`)

The arXiv full text and RAID 2025 proceedings listing were checked as a targeted follow-up. This study separates a bug's time hidden from Syzbot until it becomes findable (`D1`) from time after it is revealed but before Syzbot finds it (`D2`). Among 559 retrospectable upstream Linux bugs, it reports a mean `D1` of 331.17 days and `D2` of 73.94 days; in a random 50-bug case study, revealing factors were judged correct for 44 (88%). This changes how the 2019 report-backlog and time-to-fix evidence should be interpreted: report-to-fix alone omits time before the fuzzer can exercise the bug.

The follow-up is not a clean census: the study started with 1,159 candidates but excluded bugs that could not be reproduced or built in time; its authors explicitly say this makes `D2` likely an underestimate. It is restricted to upstream Linux bugs with fixing commits and reproducers, and reports custom historical patches. It therefore cannot be generalized directly to all kernel bugs or to the BSDs.

## Bounded findings

1. **For FPSO, smaller generated suites are not evidence of more faults found.** The sampled FPSO paper compares generated suite sizes over 30 stochastic runs and three configurations but does not execute suites against an SUT or measure faults; DPSO generally leads on size, with FPSO winning some mean-size comparisons. The 2026 CIT-metrics preprint reports metric/fault-detection correlations, including real-fault-derived cases, which narrows the gap but does not rerun or validate FPSO. A falsifiable follow-up should compare FPSO, DPSO, and non-PSO baselines on the same versioned SUTs, use verified real faults plus non-equivalent mutants, match generation and execution budgets, report every-seed suite size and fault yield, and test whether VCC predicts held-out fault detection. This claim is specific to the reviewed papers, not a universal statement that suite-size reduction is useless.

2. **A fuzzing outcome should distinguish bug reachability from discovery and repair.** The 2019 snapshot measures pending crash-report age and report-to-fix time, with unresolved reports that may duplicate bugs. SyzRetrospector later reconstructs a prior “hidden/unfindable” interval and a separate fuzzer-search interval, reporting substantial means for both; its exclusions of hard-to-reproduce bugs may bias the latter downward. A falsifiable follow-up would construct a versioned, deduplicated multi-kernel cohort and record introduction, first fuzzability/revealing change, first reproducible report, human confirmation, and fix as separate timestamps, then compare delay distributions under explicit censoring and reproduction rules. The reviewed evidence does not establish that these delays or causes transfer unchanged across operating systems.

## Scope and limitations

This is a complete audit of two sampled papers from one topic-period cell, plus two targeted full-text citation/context checks. The follow-up papers are not additional members of the frozen sample. No FPSO rerun, fault-injection campaign, kernel-history reconstruction, or independent replication was performed. Findings are bounded research leads, not novelty, prevalence, or causal claims. One follow-up preprint contains internal metadata and sample-count inconsistencies that remain unresolved.
