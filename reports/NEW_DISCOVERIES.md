# New discoveries and evidence-backed findings

## 2026-10-15: exact boundary-signature lemma proved on unweighted trees

- **Mathematical result:** For every finite connected unweighted tree, terminal set $S$, finite metric and injective terminal labeling, deleting terminal-free leaves and suppressing nonterminal degree-two paths preserves both the minimum metric-labeling cost and the crossing budget of every $k$-bounded extension. The proof is two-sided: triangle inequality maps a tree labeling to the core, and constant-on-path extension maps a core labeling back.
- **Size/exponent:** The resulting core has at most $2|S|-3$ edges for $|S|\ge2$, i.e. an explicit $O(|S|)k^0$ restricted construction. The exponent is independent of the label bound $s$; the terminal factor is not hidden. This does not settle weighted trees, cacti, or general graphs.
- **Workflow evidence:** The real theory-worker attempt created a valid structured JSON result and Markdown exposition, but it also changed the protected Supervisor script and was therefore rejected as a worker-write conflict. Independent reconciliation validated the restricted proof; the conflict is retained as a negative control for the execution path.
- **Classification:** Fully proved restricted tree lemma; no asymptotic lower bound, unrestricted theorem, or novelty claim. No experiment ran and no experiment authorization changed.
- **Next decision:** Admit a separate single-cycle cactus proof/obstruction task. If cycle composition fails, preserve the exact gap and reassess O7 without promoting it to a lower bound.

## 2026-10-15: Zero Extension theorem audit isolates a real proof gap, not a result

- **Source-matched finding:** Reidl--Wahlström's exact \(k\)-bounded metric-sparsifier theorem is \(O(k^{s+1})\) for fixed constant \(s\). The exponent arises because each edge receives an \(s+1\)-element certificate (one per gammoid layer plus the uniform layer) before representative-set compression.
- **Forward-citation correction:** The final Wahlström multicut paper retracts its preliminary 0-Extension metric-sparsifier claims because a sparse-cut argument assumed an unsupported bound on internal crossing edges. Later exact flow/cut, approximate sparsifier, and Steiner-node 0-Extension results use different preservation objects or guarantees and do not answer this question.
- **Scientific status:** No label-independent polynomial exponent has been proved or ruled out in the audited source chain through 2026-10-15. This is not a global absence claim and is not a novelty claim.
- **New proof program:** The strongest next obligation is a two-sided, label-independent boundary-signature lemma for trees/cacti. A contraction-only distinguishable-signature lower-bound construction is the fallback. Both are conjectural and must be adversarially checked.
- **Authorization boundary:** No experiment ran, no experiment budget changed, and Paper 3 Target A/B remain untouched. See [`zero_extension_theorem_and_novelty_audit_20261015.md`](zero_extension_theorem_and_novelty_audit_20261015.md) and [`proof ledger`](../research/zero_extension_proof_obligation_ledger_v1.json).

## 2026-10-15: EDCS one-flip failure generalizes mathematically, without refuting EDCS

- **Independent derivation:** A separate fixed-witness checker reproduced the queue behavior and degree arithmetic. On the fourth insertion, P2 forces `(1,0)` into `H`; this raises the old used edge `(0,0)` to degree sum `3+2=5>beta=4`.
- **Generalized result:** For every integer `beta=b>=3` with `beta_minus=b-1`, a star of `b-1` used edges followed by one cross-edge insertion creates the same obstruction. In the explicitly stated single-edge-toggle model, at least two H toggles are necessary: add the deficient edge and remove a newly violating used edge.
- **Classification:** The four-edge result is an independently reproduced finite counterexample; the parameterized statement is fully proved for this variant class; no theorem about original EDCS, HEDCS or dynamic matching has been claimed.
- **Provenance caveat:** The protocol Git commit predates execution, but the internal `frozen_at` field is later than the observed execution and validation files. Strict temporal preregistration is therefore chronology-uncertain. A later supervisor artifact-only misclassification is preserved and repaired by pointing the task to the structured report.
- **Next step:** A parameter/repair-budget/queue-policy comparison is specified but not executed; it requires a new explicit authorization.

## 2026-10-15: adversarial EDCS proof review corrected the repair claim

- **Correction:** The broad statement that a P2-deficient unused edge must be inserted into `H` is false. With `beta=4, beta_minus=2`, inserting a different unused edge can raise the deficient edge's endpoint degree and restore P2 without inserting it.
- **Surviving theorem:** Under `beta_minus=beta-1`, a degree-zero private endpoint, and exactly one H-edge insertion/deletion per update, every one-toggle outcome fails for the parameterized star-plus-cross-edge state; `beta=3` satisfies the same arithmetic. This is a restricted impossibility result, not a general repair lower bound.
- **Novelty decision:** Bernstein–Stein's alternating full/deficient repairs and bounded repair work are known prior art. EDCS is therefore closed as an independently verified educational/engineering result; no original-EDCS refutation or publishable dynamic-maintenance lower bound is claimed.
- **Next candidate:** The source-audited exact Zero Extension metric-sparsifier question asks whether the 2018 `k^(s+1)` upper-bound exponent must grow with the label parameter `s`. It remains a literature/theorem-definition lead only; no experiment or novelty claim was made.

## 2026-10-15: frozen Paper 4 action produced an explicit setup infeasibility

- **Experiment:** The pre-frozen A2 action tested a 3-independent-set postselection condition in an exact n=8 state-vector simulation on 20 seeded simple 3-regular graphs.
- **Result:** The condition had **0/20 feasible graph instances** under the preregistered distance-4 definition. This is a feasibility no-go, not a negative effect estimate. The same run's source-style A1 comparator was available on 16 graphs and had conditional mean delta **+0.3435 expected satisfied edges**, but the admitted-subset denominator and small design prevent a population claim.
- **What changed:** A candidate Paper 4 action was executed and independently validated; its assumptions were not updated after seeing the result. The result weakens the immediate A2 direction and does not validate Paper 4 planning utility.
- **Reproducibility:** [`result.json`](../results/qaoa_postselection_pilot_20261015/result.json), [`independent validation`](paper4_qaoa_postselection_validation_20261015.json), and the frozen plan hash in [`paper4_prospective_plan_v1.json`](paper4_prospective_plan_v1.json).

## 2026-10-15: Paper 3 observability expanded without creating labels

- Round 3 independently validated four source-only rows, three eligible, with zero direct resolution labels. Partial progress and missingness remain separate dimensions.
- This is a changed eligibility/observability decision and a valid no-score result. It is not evidence that the questions were unresolved, and it does not support a Paper 3 forecast metric.

## 2026-10-15: Paper 3 bottleneck is endpoint matching, not just retrieval

- Across nine unique eligible questions in the new rounds, direct labels are **0/9**. In Round 4, all three questions had authenticated or cross-checked follow-up records, yet none matched the frozen object/intervention/comparator/metric/gate tuple. In Round 5, four of six had follow-up source records, yet none matched.
- **Changed decision:** retrieval remains incomplete and must not be ignored, but the strongest supported bottleneck is that later papers usually change the intervention, comparator, endpoint, or success condition. Eligibility screening and a five-year window did not explain the zero once eligible questions were screened.
- The next cohort rule now requires source-pinned artifacts/comparators and an independently checkable endpoint before future searching. If that stronger cohort still yields zero exact matches with high authenticated coverage, the direct-label transfer is treated as infeasible under the current Paper 3 rubric.
- See [`paper3_observability_cause_diagnosis.json`](paper3_observability_cause_diagnosis.json).

## 2026-10-15: QAOA A1 sensitivity shows denominator fragility

- The independent recomputation retained all 20 graphs and verified every raw state-vector field. The strict valid-set A1 estimate is **+0.3435** expected satisfied edges on 16/20 graphs; a predeclared sensitivity coding that retains the four structural-missing rows as zero contributions is **+0.2748**, a 20% reduction.
- The four rows are structural missingness, not observed zero effects. Therefore the result is a robustness warning about the estimand, not evidence of a general postselection advantage. See [`qaoa_source_baseline_sensitivity_20261015/result.json`](../results/qaoa_source_baseline_sensitivity_20261015/result.json).

## 2026-10-15: Avocado matched endpoint is currently infeasible

- Avocado 100.0 and the public CIT plugin were pinned; constrained and empty-constraint generator smoke paths ran locally. The source-matched QEMU validation oracle, its 192 qemu-iotests scripts, the industrial five-parameter model, and an independent held-out configuration model were not available.
- **Changed decision:** no real constrained-versus-unconstrained comparison ran. Generator smoke row counts are not a scientific null result. The lead is a bounded conditional no-go until a version-pinned QEMU/model bundle exists.

## 2026-10-15: Paper 3 artifact-gated stop rule fired

- A fresh six-question cohort required source-pinned artifacts, comparators, independently checkable endpoints and falsification rules before follow-up search. Five of six had authenticated primary follow-up coverage; exact object/comparator/metric/gate matches were still **0/6**.
- **Changed decision:** stop expanding retrieval-focused Paper 3 cohorts under this rubric. No Paper 3 score or negative resolution rate is claimed. The program now requires a separately preregistered endpoint-matched experiment.
- The subsequent null-type feasibility audit authenticated the paper/package endpoint but found no usable Java 1.5-era build stack or Python-2 driver, so no mutation efficacy run was performed.

## 2026-10-15: larger-n QAOA source-style baseline remains positive in a bounded pilot

- On 20 seeded n=10 simple 3-regular graphs, all predeclared distance-3 conditioning events were feasible. The paired conditioned-minus-unconditioned expected-cut mean was **+0.1972**, with 19 positive and 1 negative graph-level differences.
- This is a local robustness observation under fixed parameters and graph generation. It does not establish a general advantage or planner utility, and the configured experiment-start budget is now exhausted.

## 2026-10-15: SERENIoT cross-device test is feasible only with new matched-device evidence

- **Changed scientific decision:** The source and follow-up audit reconciles SERENIoT's native packet-signature majority whitelist with a different follow-up host/domain policy. The follow-up supports device-disjoint evaluation as a design idea, but it does not report SERENIoT false-allow or false-block rates.
- **What is blocked:** The historical IoT Inspector corpus is not publicly downloadable from the inspected sources, the cited anonymized repository was not resolvable, and this workspace contains no matched physical-device or independently labeled attack traces. No experiment ran, and no security benefit is claimed.
- **Next falsifiable gate:** With authorized traces or a small preregistered lab dataset, compare single-device and majority-trained native signature whitelists on held-out devices; report false-block and false-allow separately with exact denominators. Either endpoint can falsify the proposed transfer benefit.
- **Evidence boundary:** This is an artifact-only feasibility decision, not a Paper 3 outcome label, a Paper 4 utility validation, or a deployment security result. See [`sereniot_cross_device_feasibility.json`](sereniot_cross_device_feasibility.json).

## 2026-10-15: control-loop audit separates artifacts from scientific success

- **Changed scientific decision:** The supervisor now requires a task-specific scientific completion gate after JSON artifact validation. `HISTORICAL-OUTCOME-001` remains `artifact_only` because no direct future-resolution or explicit-unresolved label was authenticated. The Paper 4 action-outcome artifact is scientifically complete as a descriptive provenance audit, while its planning-utility claim remains gated and unvalidated.
- **Actual action evidence:** Five prior actions were coded: 0 efficacy outcomes, 4 feasibility blockers and 1 conditional future test. There was no unified immutable pre-action ranking and no endpoint-matched efficacy sample, so no Paper 4 utility score, calibration estimate or causal benefit is reported.
- **Control-loop result:** Historical audit found one false quota classification (CAM canonical queue write) and two historical false-positive concurrent-write detections (derived lane checkpoint and launchd log). New tests cover structured quota detection, mock pause/reset recovery, canonical queue protection and artifact-only outcomes. Full audit: [`research_control_loop_audit.json`](research_control_loop_audit.json).
- **Boundary:** launchd is installed and loaded and a real kickstart increased observed runs from 3 to 4 with exit code 0; the bounded job being `not running` afterward is expected. This proves restart-capable bounded execution, not a claim of a continuously running service or scientific success.

## 2026-10-15: Paper 4 action utility remains unvalidated after real outcome coding

- **Finding:** The descriptive audit reconciled Paper 4 plans with observed feasibility/certification outcomes across CAM, Badger, DP158, uncertainty robustness and SERENIoT. The only directional plan-to-gate correspondence was Badger's prerequisite gate; the action set is heterogeneous and lacks a common timestamped ranking.
- **What changed:** The audit is now a scientifically completed negative/bounded result rather than an artifact-only failure. It strengthens the decision to require a prospective immutable plan and independent endpoint coding before any utility estimate.
- **What did not happen:** No direct historical label was fabricated, no Paper 3 metric was estimated, and no breakthrough or planning advantage was claimed.

## 2026-10-15: uncertainty-robustness direct test is currently infeasible

- **Changed scientific decision:** The original 2004.11573 source pins the KuK-style uncommon-uncertainty generation objectives and headline settings, but no versioned implementation, dataset/model bundle, matched conventional comparator, equal-example/equal-compute rule, or held-out robustness protocol was authenticated. The local machine also lacks the reported legacy stack and relevant artifacts.
- **What this rules out:** The 2023 uncertainty-guided retraining near-match cannot be promoted to direct resolution, causal robustness benefit, or a Paper 3 label. No model training, proxy experiment, synthetic labels, or hindsight relabeling was performed.
- **Reranking:** This lead is rejected as an actionable experiment for the current environment. The next bounded candidate is SERENIoT cross-device whitelist generalization, with false-allow and false-block endpoints kept separate. See [`uncertainty_robust_direct_test_feasibility.json`](uncertainty_robust_direct_test_feasibility.json).

## 2026-10-15: targeted retrieval improved observability but produced no Paper 3 label

- **Changed scientific decision:** Citation/definition tracing upgraded the 2004.11573 question from search-visible-only to a full-text-audited dated follow-up. The 2023 study is a genuine primary source, but it uses standard attack-generated examples and uncertainty-guided ordering rather than the source's uncommon-uncertainty generator, and it does not provide the frozen equal-example/equal-compute comparison.
- **What this rules out:** The follow-up cannot be used as direct resolution, refutation, or explicit-unresolved evidence. All 13 original frozen labels remain `unadjudicated`; no Paper 3 feature, training row, validation row, test score, or forecast probability was created.
- **Next falsifiable gate:** Audit source-code/data availability and exact intervention/comparator/budget feasibility for a preregistered direct test. If those inputs cannot be pinned, reject this lead rather than substituting a proxy experiment or synthetic label. See [`historical_outcome_adjudication.json`](historical_outcome_adjudication.json).

## 2026-10-15: DP158 matched-guarantee comparison is explicitly infeasible

- **Changed scientific decision:** The source-authenticated audit of the published GDP filter and the adaptive RDP fallback found that a matched comparison cannot be made defensibly with the currently available evidence. The GDP result supplies asymptotic error orders and finite-q Monte Carlo checks, but no certified finite-q `(epsilon, delta)` error enclosure. The local RDP fallback is theorem-motivated and adaptive, but its inspected implementation is deliberately conservative and ordinary floating point rather than a certified accountant.
- **What this rules out:** Raw active-step counts, utility comparisons, production undercount claims and privacy-superiority claims are not valid at unequal or uncertified guarantees. The prior finite-q Gaussian-CDF discrepancies remain numerical diagnostics only; they are not a theorem counterexample or deployed privacy failure.
- **Next falsifiable gate:** A future attempt requires version-pinned author code or fully specified scalar/vector and clipping conventions, a tighter proved per-step RDP bound, and validated interval/quadrature error enclosures. If those cannot be obtained, retain this infeasibility result and move effort to the targeted historical source gap. See [`dp158_matched_guarantee_audit.json`](dp158_matched_guarantee_audit.json).

No new breakthrough has been established by this campaign checkpoint.

## 2026-10-15: the 16-paper trajectory cohort is fully screened

- **Changed scientific decision:** The remaining six exact-version source screens are complete. The separately frozen cohort is now **16/16 source-screened: 12 eligible and 4 ineligible**. No paper was replaced after looking at later outcomes. The source-only ledger is [`historical_observable_source_screen_round6.json`](historical_observable_source_screen_round6.json).
- **Trajectory result:** Bounded follow-up checks for all 12 eligible questions yield direct resolution **0**, premise refutation/revision **0**, partial progress **5**, independent broad-premise strengthening **1**, contradiction **0**, scope narrowing/reformulation **3**, continued explicit uncertainty **0**. The 12 direct outcomes remain unadjudicated; a missing hit is not a negative label. Full provenance and exclusions are in [`historical_evidence_trajectory_round2.json`](historical_evidence_trajectory_round2.json).
- **What this rules out:** Increasing the number of source-screened papers did not by itself create a valid Paper 3 outcome dataset. The bottleneck is observable, definition-matched future outcomes, not simply article count. The original 20-paper blind cohort and its 13-question labels remain unchanged.
- **New actionable leads:** Avocado has follow-up implementation of the source's planned constraint-solver capability, but no matched constrained/unconstrained detection-cost comparison; SERENIoT follow-up makes cross-device whitelist generalization and adversarial false-allow/false-block rates the decisive missing experiment. These are leads, not discoveries.

## 2026-10-15: Paper 3 readiness and patch-explanation feasibility are negative/limited results

- **Paper 3:** [`paper3_trajectory_readiness.json`](paper3_trajectory_readiness.json) records a valid no-score decision: 12 rows, zero direct positive labels and zero direct negative labels, so no temporal holdout or forecast metric can be estimated.
- **Paper 4 transfer:** The artifact-only patch-explanation pilot passed material validation and blinding checks on two synthetic fixtures, but local environment inspection found no Defects4J CLI and no usable Java runtime. It therefore supports only a protocol/materials go decision, not a human-review effect, LLM-as-human substitute, or repair benchmark result. See [`patch_explanation_feasibility.json`](patch_explanation_feasibility.json).

## 2026-10-15: CAM feasibility is a completed conditional no-go

- **Changed scientific decision:** A real bounded worker audited the CAM source, the independent Ericsson replication and public industrial-data candidates. The artifact records a conditional no-go: currently verified public data do not jointly provide project-linked logs, multiclass cause labels and paired software artifacts for the required log-only versus log-plus-artifact comparison.
- **Endpoint protection:** The 2019 Ericsson 50% product-fault recall remains a separate binary endpoint and is not used as a direct result for the 2017 multiclass CAM question. The next experiment is allowed only after an authorized data release passes project-disjoint split, artifact-at-alarm-time and label/license gates.
- **Supervisor validation:** The first retry was blocked by a supervisor-owned queue snapshot false positive and a CLI invocation compatibility issue; both were fixed. The second real worker produced and independently JSON-validated [`cam_artifact_ablation_feasibility.json`](cam_artifact_ablation_feasibility.json). The raw failed attempt is retained under `research/worker_runs/`.

## 2026-10-15: Badger matched-CPU experiment is currently infeasible

- **Changed scientific decision:** The real bounded Badger audit pinned the 2018 source repositories, built Kelinci's native interface and confirmed `cpu.stat: usage_usec` in a disposable Linux container, but could not assemble the Java/Ant/Gradle/AFL/JPF/SPF/Z3 stack or a common subject-level cost metric. The artifact is [`badger_matched_cpu_feasibility.json`](badger_matched_cpu_feasibility.json).
- **No performance claim:** No Java benchmark, paired randomization, bug-yield measurement or Badger-versus-KelinciWCA outcome ran. The lead is a completed conditional no-go for this machine, not a negative performance result.
- **Reranking:** The next queue priority moves to the DP158 matched-guarantee audit or a targeted original-cohort source gap. A future Badger retry requires a finite offline compatible build image and one-subject calibration gate; no package installation or persistent service was started.

## 2026-10-14: historical-outcome bottleneck and separate trajectory pilot

- **Changed scientific decision:** A 13-question [retrieval/directness audit](historical_label_bottleneck_audit.json) found only four future primary full-text section checks; nine cases are too weakly retrieved to distinguish absence from search failure. All four checked near-misses differ on exact scope, assumptions or joint metric. The original zero direct labels remain unchanged. Repeating broad keyword variants is down-ranked in favor of a separately frozen, outcome-observable cohort.
- **Original-source eligibility result:** In the new 16-title cohort, targeted exact-version sections yielded one eligible [Badger](https://arxiv.org/pdf/1806.03283v1) fair-resource comparison and one ineligible completed fair-submodular result. This is a 2-paper source screen, not a population estimate. Badger's paper itself names an unequal-process/core comparison and proposes a fairer one.
- **One bounded trajectory dimension, not a breakthrough:** Independent [HotFuzz 2020](https://www.ndss-symposium.org/wp-content/uploads/2020/02/24415-paper.pdf) confirms that another cost-guided Java fuzzing approach can expose complexity vulnerabilities. Under the newly frozen rubric, this supports only a broad independent-evidence premise. It does **not** resolve Badger's matched-CPU hybrid advantage, and it is not a Paper 3 positive resolution label. [Provenance and exclusions](historical_evidence_trajectory_round1.json).
- **Still unverified:** no fair-CPU Badger run, no direct new-cohort resolution, no valid Paper 3 CS forecast metric, and no validated Paper 4 action utility. The descriptive action audit exists, while [the new action graph](paper4_badger_action_plan.json) still uses illustrative, not measured, likelihoods.

## 2026-10-14: independent industrial transfer caveat (not a direct outcome)

- **Changed scientific decision:** After separately locking the [CAM source-only question](historical_observable_source_screen_round3.json), an independent [ICSE 2019 primary paper](https://users.encs.concordia.ca/~pcr/paper/Amar2019ICSE-draft.pdf) reimplemented log-only CAM on Ericsson data. Its Table I reports 50% product-fault recall at K=15, and the authors explicitly cite skewed environmental failures as a reason for poor transfer. This prioritizes project-disjoint, class-skew-aware baseline measurement before any artifact-augmentation claim.
- **Boundary:** The frozen 2017 question asks whether added software artifacts improve held-out project-level *multiclass cause accuracy* at matched training budget. The 2019 paper measured a binary product-fault endpoint, did not add those artifacts and did not compare the frozen arms. Thus the trajectory records **partial progress and explicit scope narrowing**, not direct resolution, premise refutation or a numerically comparable contradiction. [Five-row evidence ledger](historical_evidence_trajectory_round1.json).
- **Coverage and failure:** Ten of sixteen new-cohort sources have targeted cutoff-version section screens (eight eligible; two ineligible). All eight eligible questions received bounded follow-up searches; none has a direct authenticated label. Bounded searches for the exact bounded-degree-tree coupled-task theorem and the exact [Zero Extension sparsifier-size question](historical_observable_source_screen_round4.json) found no verifiable in-window proof; this is **missingness**, not proof that either remained open. No Paper 3 forecast score or observed Paper 4 utility follows.

## 2026-10-15: repair-oriented follow-ups remain endpoint-mismatched

- **Changed scientific decision:** The source-only screen now covers **10/16** papers in the separate observable cohort: eight eligible, two ineligible, six unscreened. The 2019 explainable-repair question and 2020 DNN-repair question were retained as eligible before their follow-up searches; neither received a direct resolution label.
- **Partial progress only:** A 2023 primary study scored LLM-generated patch explanations for correctness, completeness, complexity and continuity on 30 Defects4J bugs, but did not compare patch-only versus explained presentation or measure reviewer acceptance/time. DeepDiagnosis evaluated DNN diagnosis/recommendations on 444 models, and a 2023 architecture-repair benchmark found random baselines competitive and failures on larger models; neither tested the frozen DNN-aware versus code-only repair comparison with verified regression/security outcomes. These are trajectory dimensions, not Paper 3 labels or breakthroughs.
- **Boundary:** The evidence-trajectory ledger now has eight audited questions: direct resolution 0, premise refutation/revision 0, partial progress 4, broad independent premise strengthening 1, scope narrowing/reformulation 2. These counts are descriptive and non-independent; no prevalence or forecast metric is reported.
- **Partially executed action, negative feasibility result:** The [Badger dependency inventory](badger_feasibility_initial.json) pinned public source commits and tested host plus a cached offline Java container. Host Java/Ant/Gradle/AFL are absent; container JDK21 exists but Ant/Gradle and pinned JPF/SPF/Z3/AFL integration remain unverified. No benchmark was run. This changes priority toward a bounded build/metric gate and cheaper cohort screening, but does not validate Paper 4's predicted information gain.

The blind historical cohort now has 20/20 original-version source-section screens and 13 source-grounded candidate questions (seven excluded); see `reports/historical_source_screen_round1.json` and `reports/historical_source_screen_round2.json`. This is a screening-yield observation, not a direct future outcome, verified novel result, or Paper 3 forecast validation.

The first bounded future-evidence triage searched all 13 questions but authenticated no direct resolution or explicit-unresolved label. Its near-matches are deliberately excluded, particularly the 2024 unmarked cycle-packing result versus the marked-vertex question. See `reports/historical_blind_followup_triage_round1.json`. Missing search hits are not negative scientific outcomes.

## Literature-supported observations

- **Finding 155:** Controlled review evidence is defect-class-specific; a separate field study's post-review-fix proxy is observational and does not establish review causality. The transport/measurement gap is a study design lead. Sources and caveats are in `data/research_findings_batch76.jsonl` and `docs/fulltext_audit_batch76.md`.
- **Finding 156:** Developer-reported adoption/usability evidence is not a verified security-outcome estimate. See the same batch76 finding/audit artifacts.
- **Finding 157:** Private dependence tests, directed local-privacy leakage analysis, and distribution-shift concerns exist, but their threat models differ. Dependence detection is not a direct leakage measure. See batch77 artifacts.
- **Finding 158:** Adaptive privacy-filter guarantees have operating-regime conditions; a guarded fallback is a bounded implementation lead, not a new theorem. See batch77 artifacts.

## Executed empirical results already in the repository

- The synthetic four-case Paper 5 executor pilot is an infrastructure smoke test only; its cases are hand-authored and do not establish real research-agent effectiveness.
- The DBMS operational campaigns ran real pinned SQLite/NoREC tooling. The short-run SQLancer++ pairs were operationally null; the subsequent 5-seed longer run showed positive query-pair proxy differences. There are incomplete SQLancer seed runs, derived/rounded-rate concerns, and no independently confirmed distinct logic bug. See `docs/dbms_guidance_campaign.md`, `results/dbms_guidance_campaign_v3/summary.json`, and `results/sqlancerpp_feedback_long_campaign/summary.json`.

## New reproducible operational result (not a breakthrough)

- **Fresh-seed SQLancer++ proxy replication:** On predeclared unused paired seeds 4111–4115, the feedback-on arm exceeded feedback-off by 265, 346, 407, 265, and 299 successful query pairs under the pinned 20-database/200-attempt-per-database setup. An independent parser rederived each numerator from all retained per-database rates; the pinned source prints the direct ratio. All five pairs were complete and all used the same source commit, jar hash, image digest, and SQLite 3.40.0. Two-sided exact sign test p=0.0625 (one-sided directional p=0.03125). This is reproducible evidence for a narrow operational proxy effect in this setup only—not bug yield, a Paper 3 forecast, Paper 4 utility, agent effectiveness, or a novel scientific contribution. Raw logs and analysis are under `results/sqlancerpp_feedback_replication_4111_4115/`.

## Negative and unresolved results

- No DBMS run has a confirmed distinct logic bug.
- Paper 3 has not yet produced a historically valid CS forecast evaluation.
- Paper 4 action outcomes have now been coded descriptively, but planning utility has not been scored or validated because the common pre-action ranking and efficacy endpoint sample are missing.
- The study has not yet established matched-CPU superiority or any increase in independently confirmed distinct logic bugs.

## Additional pre-registered CPU-normalized operational result

- **SQLancer++ feedback throughput, seeds 4121–4125:** all five paired runs completed with cgroup-v2 CPU usage counters. The feedback-on minus feedback-off differences were +93.15, +43.99, +86.75, +73.08, and +57.34 successful query pairs per CPU-second (mean +70.86; exact sign test two-sided p=0.0625). Run order was always off then on, so time/order effects remain possible. This is not an equal-CPU allocation experiment, bug-yield result, or evidence of distinct bugs. Independent parser and per-arm raw metadata: `results/sqlancerpp_feedback_cpu_4121_4125/independent_analysis.json`.

## Literature evidence update (not a new discovery)

- Batch 34's two previously identifier-less citation-follow-up papers now have downloaded, hash-verified official PMLR full texts. The 2023 active-membership-inference paper reports attacks under its explicitly malicious-server threat model and studied LDP mechanisms; it sharpens the threat-model/measurement gap for finding 157, but does not refute LDP universally. The 2013 arXiv crowdsourcing paper is officially withdrawn and unavailable as a PDF, so its old abstract claim is excluded. See `docs/fulltext_audit_batch34.md` and `reports/fulltext_batch_recovery.json`.

This file is intentionally sparse. Only verified raw experiment outputs can add new empirical discoveries; literature-derived claims remain labeled as such.

## 2026-10-15: fresh original-CS discovery attempt is frozen, not yet executed

- **Observed evidence:** The authorized QAOA line was closed after independent n=10 conditional replication (+0.1807 expected-cut units, 20/20 positive graph units) and a negative equal-preparation end-to-end result (postselection −0.1516 best-cut units versus standard sampling over 20 graph units). The result is retained as an independent reproduction plus a fair-cost negative, not a breakthrough.
- **New scientific decision:** A source-level audit outside the exhausted directions compared four candidates. EDCS lazy local repair was selected conditionally because it has a precise invariant/counterexample endpoint, public prior-art anchors and a low-cost exact-search path. Dynamic matching is the fallback. CERT/SQLite and Oxide were rejected before execution for endpoint and dependency reasons. The [candidate ledger](novel_cs_opportunity_pool_20261015.json) records these boundaries.
- **Paper 4 boundary:** Three actions were frozen with explicit cost/information-gain assumptions and simple baselines. The ranking is prospective planning only; no planner superiority or expected-utility calibration is claimed. The previous QAOA action-selection failure remains negative historical evidence.
- **Authorization gate:** No EDCS experiment ran. The proposed bounded study is exactly one process, no network, Python 3.12, <=120 CPU seconds and <=1024 MiB; it would enumerate n<=6 cases and deletion sequences <=6, extending to n<=8 only if the first gate passes. The task is blocked in the canonical queue until explicit renewed local experiment authorization. Lifetime experiment counters were not reset or incremented.
- **Novelty boundary:** A finite search finding would be a counterexample only after minimization and independent recomputation; survival would not prove the invariant. A source-level novelty check is not a novelty claim.

The separate [Paper 3 Target B protocol](../research/paper3_target_b_protocol_v1.json) is frozen for future evidence-growth evaluation. The original direct-resolution cohorts and their no-score status are unchanged; missing follow-up evidence is not relabeled as negative progress.

## 2026-10-15: independently verified EDCS lazy-repair counterexample

- **Frozen claim tested:** With `beta=4`, `beta_minus=3`, and at most one local H-edge flip per graph update, the proposed lazy repair should preserve P1/P2 and the finite `mu(H)/mu(G) >= 2/3` endpoint.
- **Actual result:** The first minimal witness is four insertions: `(0,0)`, `(0,1)`, `(0,2)`, `(1,0)`. After the last update, used edge `(0,0)` has `d_H(L0)=3`, `d_H(R0)=2`, and degree sum `5`, violating P1's upper bound `4`. The exact matching oracle gives `mu(G)=2`, `mu(H)=2`, ratio `1.0`.
- **Coverage:** 530 static masks, 79,209 deletion prefixes, 1,165,122 deletion-update states, plus the fixed mixed trajectory; total independent checks 1,167,465. The separately implemented checker matched the runner and replayed/minimized the first failure.
- **Scientific interpretation:** This is a genuine negative result against the frozen variant. It is not a counterexample to the original EDCS theory or Bernstein–Stein's different maintenance algorithm, and it is not a new theorem. The result narrows the design space: one-flip local repair cannot be used with this invariant and parameter choice without additional global/queued repair semantics.
- **Paper 4:** The selected action was feasible within 53.98 seconds and produced substantial bounded uncertainty reduction. One action outcome cannot establish planner superiority or calibrate the original Paper 4 scores; those assumptions remain unchanged.
- **Authorization boundary:** The single authorized experiment is consumed. No further EDCS or other experiment is scheduled in this cycle.

## DP158 numerical reproduction and corrected negative lead

- **Source-matched scalar Figure 12 simulation (exploratory, not a new breakthrough):** Using the paper's explicit small-`q` budget formula at `q=0.1`, an independent million-path-per-arm implementation obtained P/Q halt rates **0.988712 / 0.987891** versus the published **0.9886 / 0.9880**; mean active steps **113.136 / 113.149** versus **113.1**. PLRV moments and empirical Gaussian-CDF discrepancies are recorded in `results/dp158_filter_source_matched_q01/independent_analysis.json`. The first exact-KL preregistration was withdrawn after source review; this run is explicitly exploratory. It does not verify a theorem, establish a new privacy bound, or audit deployed code.
- **Retracted interpretation:** A previous 100,000-path-per-arm dimension sweep looked material, but it modeled a hypothetical vector output with exact one-step KL. Appendix G.2 writes `y_i²` without clarifying scalar output versus vector shorthand, and the paper explicitly defines a different approximate `Budg`. Thus this sweep is **not** evidence of an omitted output dimension or a paper reproducibility gap. The raw results and correction remain in `results/dp158_filter_dimension_sensitivity/summary.json` and `research/experiment_preregistration_dp158_dimension_sensitivity.md` for auditability.
- A valid fully adaptive fixed-order RDP-filter theorem is available as a baseline, but no production implementation or matched accountant comparison has yet been pinned. The current status and source links are in `reports/dp158_accountant_audit.json`.

## 2026-10-15: QAOA conditional replication did not survive fair shot-cost scoring

- **Independent replication:** A new seed (20261016) and 20 new n=10 simple 3-regular graphs retained all units. The frozen A1 postselection rule produced a mean conditioned-minus-unconditioned expected-cut delta of **+0.1807** (sample SD 0.1170, descriptive SE 0.0262), with 20/20 positive graph deltas and conditioning probability 0.25.
- **Changed scientific decision:** The conditional state-quality effect is reproducible under this exact local convention, but the complete procedure is not practically superior under the declared shot budget. With 400 state preparations per procedure, postselection kept about 100 samples and discarded about 300; its best-cut outcome was **−0.1516** relative to standard sampling on average, and it beat standard sampling on 0/20 graph units.
- **Boundary:** Physical runtime is not identifiable from exact state-vector simulation. The result is a bounded reproduction/extension, not quantum advantage, hardware speedup, Paper 4 planning validation, or a new breakthrough. The original A2 action remains a setup-feasibility failure and was not rewritten.

## Equal-CPU DBMS falsification checkpoint

- **No demonstrated bug-yield gain:** Five fresh SQLancer++/SQLite 3.40.0/NoREC pairs (seeds 4131–4135) ran in balanced on/off order, each arm stopped after at least 4.5 million cgroup CPU microseconds with less than 3% overshoot. Raw failure logs and stderr contained **no NoREC mismatch candidate**, hence zero observed independently confirmed distinct bugs in these short runs. No superiority or equality conclusion follows for rare bugs.
- **Secondary operational proxy weakened:** Successful query pairs from fully completed databases differed by **+25, +51, +228, +393, −15** (feedback-on minus off; mean +136.4; two-sided exact sign *p*=0.375). The interrupted database's partial attempts were excluded. The 4/5 direction is compatible with the earlier narrow throughput proxy, but weaker than the fixed-order 5/5 runs and is **not** bug yield. See `reports/dbms_equal_cpu_result.json` and the independent reparser output.

## DP158 approximation-boundary diagnostic (known limitation, not a new theorem)

- With the paper's small-`q` budget and a frozen one-dimensional adaptive schedule, one million PLRV trajectories per P/Q arm gave maximum Gaussian-CDF discrepancies **0.01463, 0.02815, 0.04813, 0.09218** at `q=0.1, 0.19, 0.3, 0.5`. Each higher-`q` increase crossed the preregistered 0.01 materiality threshold after simultaneous DKW Monte Carlo uncertainty; `q=0.19` crossed narrowly. Stop rates stayed near 99%, so halt frequency is not a proxy for Gaussian approximation quality in this model. The source paper already anticipates weaker accuracy away from its asymptotic regimes. This is **not** a theorem counterexample, a validated guard threshold, or a deployed-accountant vulnerability. See `results/dp158_regime_boundary/summary.json` and `reports/dp158_accountant_audit.json`.
