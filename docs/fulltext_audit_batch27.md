# Full-text audit batch 27: repair and verification evidence is pipeline- and label-dependent

Updated 2026-10-12. This batch checks the ten unread uniform-random keys in `program_repair_verification`. Nine resolve to individual research papers whose sampled full-text versions were audited. The tenth is an arXiv proceedings-volume record. After identifying that mismatch, the six papers in the open volume were read as separately labeled citation follow-ups; they do not replace or enlarge the random sample. Two other random-frame keys in this cell were audited earlier (1707.05172 in batch 9 and 2503.09217 in batch 8), so the 12/12 frame keys are accounted for, including one proceedings-level item.

## 2010–2014

### 1. Mining Software Repair Models for Reasoning on the Search Space of Automated Program Fixing (2013; sampled v1)

[Martinez and Monperrus, arXiv:1311.3414v1](https://arxiv.org/abs/1311.3414); [exact sampled PDF](https://arxiv.org/pdf/1311.3414v1), §§II–V and threats to validity.

This is an empirical study of change patterns and a mathematical analysis of how repair heuristics traverse a candidate-patch search space. The authors analyze 89,993 version-control transactions from 14 Java repositories; 62,179 transactions include Java changes and yield about 1.2 million AST edits. They contrast 41 coarse change types with 173 fine-grained change-type/entity combinations. The probabilities learned from the selected transaction bags then affect the *modeled number of repair attempts* needed to find a repair shape; the paper analyzes 23,048 small fix transactions and varies both granularity and heuristics.

**Boundary:** this is not an end-to-end repair system comparison or wall-clock runtime measurement. The authors explicitly say their fix-transaction classifier is intended to approximate a repair-action distribution, not optimize classification precision/recall. They also warn that small-transaction filters may omit parts of larger fixes, and that 14 Java projects may not generalize to all Java or other languages. The key result is that search-space priors depend on representation and sampling—not that a specific repair tool fixes more real bugs.

### 2. Alternation in Quantum Programming: From Superposition of Data to Superposition of Programs (2014; sampled v1)

[Ying, Yu, and Feng, arXiv:1402.5172v1](https://arxiv.org/abs/1402.5172); [exact sampled HTML](https://arxiv.org/html/1402.5172v1), §§2–8 and appendices.

QGCL is a proposed quantum extension of guarded-command programming. The paper defines quantum alternation/choice, denotational and weakest-precondition semantics, derives algebraic laws, and illustrates the constructs using quantum-walk-style examples.

**Boundary:** this is a language/semantics contribution, not an automated program-repair evaluation. Examples establish expressiveness; the paper does not report an implementation benchmark, defect-repair rate, or comparative verification workload. It belongs in a broad programming-languages/formal-methods map, but should not be pooled with APR outcomes.

### 3. Using Formal Specifications to Support Model Based Testing ASDSpec: A Tool Combining the Best of Two Techniques (2014; sampled v1)

[van der Meer, Kherrazi, and Hamilton, arXiv:1403.7257v1](https://arxiv.org/abs/1403.7257); [exact sampled PDF](https://arxiv.org/pdf/1403.7257v1), §§3–7.

ASDSpec translates interface models from Analytical Software Design into Microsoft Spec Explorer models, joining static design verification with dynamic model-based tests. In a container-terminal case study, the authors report 89 tests from a manually constructed Spec Explorer model and 93 from ASDSpec-generated models under the compared generation strategies.

**Counterweight and boundary:** the paper estimates 28 hours for earlier model/test construction and 16 hours to reconstruct ASDSpec models, but says the estimates are not directly comparable because prior work was reused. Generated tests are based on interface models, not all system-specific properties; the authors say this limits flexibility. This is a single industrial-size case study and a test-generation comparison, not a general repair-success result.

## 2015–2019

### 4. Proceedings 4th International Workshop on Engineering Safety and Security Systems (2015; sampled v1)

[arXiv:1506.03250v1 record](https://arxiv.org/abs/1506.03250); [open proceedings volume (EPTCS 184)](https://cgi.cse.unsw.edu.au/~rvg/eptcs/Published/ESSS2015/Proceedings.pdf), cover, preface, and contents.

The sampled arXiv record is an edited proceedings volume, not an individual research paper; arXiv says no PDF is attached to that record. The official open volume contains 99 pages, six selected papers from 15 submissions, two invited-talk abstracts, and front matter. Its six papers cover MIRELA waiting behavior, railway interlocking verification, cut-set generation, hybrid-system stability, real-time function blocks, and cyber-physical systems.

**Disposition:** this item is retained as a sampled-frame record and excluded from paper-level effect synthesis. All six included papers were subsequently read and recorded separately as citation follow-ups below. This remains a data-unit mismatch requiring correction/stratification in future corpus screens; the follow-ups do not silently replace the random draw.

### 5. Scheduling Constraint Based Abstraction Refinement for Multi-Threaded Program Verification (2017; sampled v2)

[Yin et al., arXiv:1708.08323v2](https://arxiv.org/abs/1708.08323); [exact sampled HTML](https://arxiv.org/html/1708.08323v2), §§3–7.

Yogar-CBMC initially relaxes the scheduling constraint in bounded model checking, then validates/refines infeasible counterexamples. On the SV-COMP 2017 concurrency suite it solves all 1,047 programs, scores 1,293, and reports 1,550 seconds and 43 GB, versus 9,820 seconds/104 GB for Lazy-CSeq-Abs, which also solves all examples. The paper proves soundness/completeness relative to the chosen loop-unwinding depth.

**Boundary and counterevidence:** these are substantial benchmark results, but only for shared-variable, sequentially consistent programs under bounded unwinding and the SV-COMP workload. The paper itself warns performance may be worse when scheduling constraints are not the dominant formula cost, and tool/parameter comparisons are difficult to make absolutely fair. One constraint-based refinement path is never invoked in the tested suite, so behavior there is not empirically established.

## 2020–2024

### 6. Low Cost High Integrity Platform (2020; sampled v1)

[Lecomte et al., arXiv:2005.07191v1](https://arxiv.org/abs/2005.07191); [exact sampled HTML](https://arxiv.org/html/2005.07191v1), platform architecture and verification description.

This paper describes the CLEARSY Safety Platform: B-method models are proved and compiled into two diverse binaries, which execute on separate microcontrollers with runtime comparison and a safe shutdown mode. It reports that platform building blocks had been certified in named railway deployments.

**Boundary:** this is a platform/experience description, not a new controlled comparison of cost, defect rate, or certification time. The prior deployments are cited as context; the paper’s claims about shortened development and reduced testing are not supported here by a controlled before/after dataset. Several authors are affiliated with the platform vendor, so independent replication would be useful.

### 7. A Deductive Verification Framework For Higher Order Programs (2020; sampled v1)

[Soares, arXiv:2011.14044v1](https://arxiv.org/abs/2011.14044); [exact sampled HTML](https://arxiv.org/html/2011.14044v1), §§1–4 and case studies.

This prototype translates effectful higher-order OCaml programs annotated with GOSPEL assertions into first-order WhyML using defunctionalization, then calls Why3 provers. Small worked examples have verification conditions automatically discharged, and the paper demonstrates translation rules on several case studies.

**Boundary:** the evidence is feasibility of the translation/proof pipeline, not a broad performance or success-rate evaluation. The paper does not compare a large real-world program set, quantify annotation effort, or establish which higher-order/effect patterns are unsupported. It is relevant formal-verification work, but not automated repair.

### 8. MUFIN: Improving Neural Repair Models with Back-Translation (2023; sampled v1)

[Silva et al., arXiv:2304.02301v1](https://arxiv.org/abs/2304.02301); [exact sampled PDF](https://arxiv.org/pdf/2304.02301v1), §§3–5.

MUFIN iteratively trains a fixer and a breaker, using code critics to create self-supervised buggy/fixed pairs. It generates more than half a million training pairs. On QuixBugs (39 bugs) and Defects4J (428 bugs), its table reports 6/7 and 28/62 correct/plausible repairs, compared with 2/4 and 16/43 for its matched baseline. “Plausible” means the benchmark tests pass; “correct” means manually judged equivalent to the developer patch. The comparison deliberately assumes perfect fault localization to isolate patch generation.

**Counterweight and boundary:** perfect localization is an oracle unavailable in ordinary deployments; the authors restrict data to single-hunk Java bugs because their neural models struggle with multi-location bugs. Test passing and equivalence to the historical developer patch are distinct correctness proxies. This is a useful controlled gain in patch generation, not end-to-end evidence including localization or broad repository transfer.

## 2025–2026-through-cutoff

### 9. Ownership Refinement Types for Pointer Arithmetic and Nested Arrays (2026; sampled v1)

[Fujiwara et al., arXiv:2604.22361v1](https://arxiv.org/abs/2604.22361); [exact sampled HTML](https://arxiv.org/html/2604.22361v1), §§3–6 and appendices.

The authors extend an ownership/refinement type system so pointer arithmetic can be verified over nested arrays, prove the extended type system sound, and implement a verifier. It verifies a suite of matrix-like programs, including non-rectangular and multidimensional cases that the compared prior implementation cannot handle. Reported verification times range from seconds to about six minutes; the matched comparison also shows sensitivity to Z3 version and workload.

**Boundary:** the result is a formal guarantee for the stated language/type system plus a hand-designed benchmark suite, not proof about arbitrary C programs or production workloads. The system still needs richer type annotations; the authors leave improved inference for future work. The distinction matters: a soundness theorem and a small benchmark answer different questions from repair rate or large-scale deployment.

### 10. Agentic Proving for Program Verification (2026; sampled v1)

[Sosso, Arora, and Spitters, arXiv:2605.23772v1](https://arxiv.org/abs/2605.23772); [exact sampled HTML](https://arxiv.org/html/2605.23772v1), §§2–5 and appendices.

The paper evaluates Claude Code on CLEVER, a 161-problem Lean 4 benchmark adapted from HumanEval. It reports 95.7% end-to-end success over two prompt variants; after removing four benchmark-issue entries, it reports 98.1% on the remaining self-consistent premises. Crucially, the authors identify ground-truth specification problems in 80 of 161 entries and explain that some natural-language tasks permit multiple defensible interpretations. Lean compilation and proof checking are strong evidence that the produced term proves the formal statement; they do not by themselves prove that the statement matches user intent.

**Counterweight and boundary:** the benchmark is small and its entries were emended during experimentation; the headline 98.1% is conditional on removing known benchmark-issue cases, while the 95.7% figure is the broader two-run result. The paper’s strongest methodological lesson is benchmark/specification quality, not a universal claim that program verification is solved. Independent human-intent adjudication and fresh, contamination-resistant tasks remain necessary.

## Cross-paper findings (bounded to this frame cell)

### Finding A: repair scores are conditional on upstream localization, test oracles, and code representation

The earlier fault-space study (batch 9) shows GenProg's repairability/search cost changes with localization quality; MUFIN gains when localization is assumed perfect; and the transformed-Defects4J study (batch 8) reports large drops after semantics-preserving code transformations. These results point to a coupled pipeline: patch generator quality cannot be inferred from a single benchmark score without stating localization, tests, representation, and correctness oracle. They do **not** prove all reported APR gains are artifacts: MUFIN's matched-baseline setup isolates a real patch-generation contribution, and fault localization was held perfect for a stated control purpose.

**Falsifiable follow-up:** across multiple Java and non-Java repositories, factorially vary localization quality, test-suite strength, and semantics-preserving transformations while holding patch generator and compute fixed. Score compilation, test plausibility, independent semantic correctness, regression safety, and wall-clock cost separately. The hypothesis weakens if generator rankings and success remain stable across these upstream conditions.

### Finding B: “proof success” needs separate checks for proof validity and specification intent

The 2026 agentic-proving paper shows that a compiler-checked proof can expose benchmark and specification defects; it flags issues in 80/161 reference tasks and reports 98.1% only after removing four benchmark-issue entries. The 2026 ownership-types paper complements this with an explicit soundness proof and bounded benchmark experiments; the 2017 checker states its guarantee relative to loop depth. These are not interchangeable with anecdotal examples or a model's self-assessment. A rigorous evaluation should report proof checking, specification adequacy, assumptions/bounds, and benchmark-cleaning rules separately.

**Falsifiable follow-up:** assemble fresh tasks with independent human intent adjudication, machine-checkable specifications, and seeded benchmark defects. Compare raw proof-check rate with intent-preserving correctness and downstream behavior. The hypothesis weakens if checked proofs against existing specs predict intent-correct behavior equally well without independent spec adjudication.

### Finding C: the retrieval label is an umbrella, not one outcome family

In the 12 fixed random-frame keys labeled `program_repair_verification`, the work spans APR/search priors, formal verification, model-based testing, functional safety platforms, quantum-language semantics, and one proceedings-volume metadata record. Even the core APR papers measure different endpoints: modeled search attempts, fault-location sensitivity, plausible/test-passing patches, manually judged patch correctness, and robustness to code transformations. Pooling these values into one trend would be invalid. The proceedings row is a data-unit issue: one sampled arXiv ID points to a volume, not a standalone article.

**Falsifiable follow-up:** re-label a probability sample of corpus records with independent human multi-label annotations; report per-label precision/recall, proceedings/survey/software/data-record rates, and disagreements. The current-screen concern is weakened if the topic tags show high inter-rater agreement and low cross-family contamination on a larger blinded sample.

**Sampling boundary:** these are 10 newly audited/dispositioned uniform-random frame keys plus two previously audited keys, not a prevalence estimate of all program-repair or verification research. Strata are by first arXiv submission date. The proceedings record is not a standalone paper; its six constituent papers are separately audited follow-ups, not additional random-frame observations.

## Proceedings follow-up: six component papers (not random-frame additions)

The official [EPTCS 184 proceedings volume](https://cgi.cse.unsw.edu.au/~rvg/eptcs/Published/ESSS2015/Proceedings.pdf) contains six selected papers. I checked each paper's abstract, methods/case-study or results sections, and conclusion/limitations. These are useful evidence about the breadth and boundaries hidden by the sampled proceedings record, but they do not count as six more random draws.

1. **Indefinite waitings in MIRELA systems** (pp. 5–18; [DOI](https://doi.org/10.4204/EPTCS.184.1)). A translation to PRISM classifies local deadlock, starvation, and unbounded waiting. The demonstration covers two examples; changing render timing removes a starvation case. Reported runtimes depend on carefully chosen timing constants with a large gcd, and stochastic or more structurally complex systems are future work. This is a model-checking feasibility result, not broad-scale validation.
2. **Verification of railway interlocking systems** (pp. 19–31; [DOI](https://doi.org/10.4204/EPTCS.184.2)). Application data for one station (14 routes, 7 points, 7 track circuits) is translated to NuSMV; 132 invariants and 7 CTL properties are checked, including injected data errors. The paper reports about 10 hours to develop seven CTL formulas versus 100 hours with NuSMV in its route-incrementing experiment. The authors limit the evidence to one relatively small interlocking and safety properties; liveness and larger interacting systems remain open.
3. **Automatic Generation of Minimal Cut Sets** (pp. 33–47; [DOI](https://doi.org/10.4204/EPTCS.184.3)). For the A320 hydraulic example, systematic generation takes 13 minutes versus 65 minutes for the naive strategy, with the same cut-set result on the reported laptop. The workflow still assumes an analyst has identified/injected the relevant fault modes; comparison with prior SAL work is explicitly not controlled. It is one model-specific case, not a general fivefold speedup claim.
4. **Breaking Dense Structures: Proving Stability of Densely Structured Hybrid Systems** (pp. 49–63; [DOI](https://doi.org/10.4204/EPTCS.184.4)). A graph-relaxation step helps decomposition-based Lyapunov proofs on dense hybrid automata. For complete K5 and Spidercam examples, reported proof effort falls from 13h22m to 0.05s and from 1h46m to 0.06s, respectively; the cruise-controller example takes 0.060s either way. Relaxation is conservative and can introduce spurious trajectories; when too loose, the method reconstructs the model stepwise and can fall back toward the original effort. Large speedups are therefore model-structure-dependent.
5. **Formal Verification of Real-Time Function Blocks Using PVS** (pp. 65–79; [DOI](https://doi.org/10.4204/EPTCS.184.5)). Two nuclear-industry function-block case studies use tabular requirements and PVS; formalization exposes an initialization failure and a missing implementation assumption. The paper gives concrete defect-finding evidence, but not a controlled comparison of defect rates, cost, or certification time across projects.
6. **Using Indexed and Synchronous Events to Model and Validate Cyber-Physical Systems** (pp. 81–95; [DOI](https://doi.org/10.4204/EPTCS.184.6)). The TTM language adds indexed and synchronous events and is demonstrated on train-control and nuclear shutdown models. A nuclear example illustrates that ideal instantaneous synchronization can overstate behavior; separating plant/controller actions and adding a bounded response-time property changes the model obligation. These are modeling/validation demonstrations; they do not establish deployment failure reduction or broad industrial scale.

### Follow-up finding: verification speedups are structural and endpoint-specific

The proceedings papers provide real counterexamples to any blanket claim that formal verification is only theoretical: one railway case detects injected application-data errors, PVS case studies expose requirement/implementation problems, and several tools report large within-model runtime reductions. But those gains vary sharply by model: dense K5 and Spidercam benefit dramatically from relaxation while the cruise-controller example is unchanged; MIRELA's runtime depends on timing constants; and the aircraft cut-set comparison assumes analyst-specified fault modes. These should not be summarized as a general speedup for “formal methods.”

**Falsifiable follow-up:** preregister a suite of industrially sourced models spanning graph density, timing granularity, property family, and model size; compare each proposed abstraction/relaxation to the same baseline on fixed hardware and tool versions. Report proof/property coverage, correctness of abstraction, runtime, memory, human modeling effort, and fallback rate. The structural-dependence hypothesis weakens if gains remain similar across these strata and independently maintained models.
