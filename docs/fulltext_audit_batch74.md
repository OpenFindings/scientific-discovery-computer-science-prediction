# Full-text audit batch 74 — program repair and verification, 2010–2014

## Scope and provenance

This closes the frozen six-version cell `program_repair_verification × 2010–2014`: three lexical-priority versions read in this batch and three uniform-random versions previously read in batch 27 and reconciled here. The lexical screen was a retrieval heuristic, not a finding that all three papers are studies of automated program repair. In fact, the cell crosses repair, requirements engineering, medical-device execution, quantum programming, software-repair search-space mining, and model-based testing. The six papers are not pooled into a single effect estimate.

New PDFs were fetched from the exact arXiv versions and locally text-extracted (39 pages total). Detailed per-paper provenance is in `data/fulltext_review_ledger_batch74.jsonl`.

## New full-text reads

### Distributed Real-Time Emulation of Formally-Defined Patterns for Safe Medical Device Control (1009.4266v1)

The paper formalizes reusable command-shaper patterns in Real-Time Maude and describes mapping logical-time models into physical-time emulations. In its pacemaker scenario, a formally verified pattern is connected to a Java pacemaker simulator, not a clinical pacemaker; measured control jitter is mostly below 0.1 seconds and almost never above 0.2 seconds on the stated 1.67 GHz Windows/Cygwin setup. In the second case, the model commands a physical Multi-Phaser NE-500 syringe pump; a scale trace is used to check one execution against bolus-duration/frequency constraints. The paper explicitly depends on timing bounds and tolerable jitter, and says network-disconnection/open-loop safety and other device safety classes remain unaddressed. These are proof-plus-emulation feasibility demonstrations, not clinical outcome evidence or a general guarantee across devices.

### Requirements Engineering Methods: A Classification Framework and Research Challenges (1203.1717v1)

This is a conceptual taxonomy of requirements-engineering methods (REMs), organized around five components: requirements problem/solution, ontology, formalism, organization mechanism, and guidelines. Its stated goal is to aid analysis, teaching, extension, design, and validation. It explicitly treats systematic validation of REMs as an open research challenge and says its framework is limited: it supplies a checklist and points toward component-specific validation methods, but does not itself prescribe which concepts are relevant or establish empirical effectiveness. This is a framework proposal, not an outcome study.

### A Critical Review of “Automatic Patch Generation Learned from Human-Written Patches” (1408.2103v1)

This argumentative essay distinguishes repair settings and defect classes, then explains why “correct,” “understandable,” and “complete” are not interchangeable patch criteria. A test-suite-based repair result is relative to the tested behavior and the repair scenario; recommendation systems may permit partial fixes and require developer comprehensibility, while fully automatic/runtime repair has different obligations. Patch acceptability can be underdetermined when behavior is unspecified. Its contribution is conceptual/methodological critique, not a new empirical estimate. The paper itself concludes that defect-class characterization and explicit problem/evaluation definitions are necessary to avoid misleading claims.

## Reconciled random arm

The other three frozen versions are already fully read in batch 27 and were not re-counted as new reads: 1311.3414v1 models repair actions/search spaces from repository transactions (modeled effort, not end-to-end measured runtime); 1402.5172v1 gives formal semantics for quantum programming (not an APR outcome study); and 1403.7257v1 compares model-based test generation in one container-terminal case study, with effort figures that are not directly comparable because prior work was reused. The exact earlier evidence notes and audit links are carried into this batch's six-row ledger.

## Bounded findings and next tests

### Finding 150 — Repair “success” is conditional on oracle and intended use

The 2014 essay already rejects a single context-free patch-correctness criterion. Later primary empirical studies support the practical importance of this boundary: a QuixBugs study manually classified 53.3% of 338 plausible generated patches as overfitting, while a 2019 study found test-suite repair performance varied substantially by benchmark (21% of bugs patched across five benchmarks, with 47% on Defects4J versus 10–30% on the others). A later patch-assessment study also shows assessment tools can misclassify patches when generated tests violate implicit preconditions. This is established methodological risk, not a novel discovery from this small historical cell. The useful follow-up is to make every repair claim explicit about defect class, oracle, benchmark, intended use (recommendation vs automatic deployment), and patch acceptance rule.

### Finding 151 — Formal proof survives only through stated timing and implementation assumptions

The medical-device paper connects a verified model to a simulated pacemaker and a physical syringe pump, but its examples require timing/jitter assumptions and cover only selected safety patterns and scenarios. It explicitly excludes open-loop/network-failure safety and does not demonstrate clinical deployment. A later CPS testing paper independently argues for simulation, hardware-in-the-loop, and field validation because simulation coverage/fidelity and requirement traceability can be inadequate; that is adjacent-domain counterevidence, not proof that the same gaps occur in medical devices. The bounded research lead is end-to-end assurance across model, generated/adapter code, timing, communication failures, hardware, and operational scenarios, rather than “formal verification has not been combined with testing.”

### Finding 152 — A taxonomy is not evidence that a method works

The REM classification framework identifies components and validation questions but explicitly says it does not resolve what concepts are relevant or provide a complete validation procedure. The methodological gap is therefore not the absence of taxonomies; it is demonstrating, for a particular method and stakeholder context, that its requirements coverage, consistency handling, and decisions improve downstream outcomes. Test one REM prospectively against a baseline with independent stakeholder tasks, traceability/completeness measures, and decision quality; do not infer effectiveness from framework completeness alone.

## Limitations

This is one six-record, retrieval-stratified historical cell with three newly read lexical-priority records; the three random records were previously audited. Topics and outcome definitions are heterogeneous. The follow-up studies are targeted counterevidence, not an exhaustive systematic review, and cross-domain CPS findings cannot be treated as direct medical-device evidence. No global novelty claim is made.
