# New discoveries and evidence-backed findings

No new breakthrough has been established by this campaign checkpoint.

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
- Paper 4 action utility has not yet been scored against real action outcomes.
- The study has not yet established matched-CPU superiority or any increase in independently confirmed distinct logic bugs.

## Additional pre-registered CPU-normalized operational result

- **SQLancer++ feedback throughput, seeds 4121–4125:** all five paired runs completed with cgroup-v2 CPU usage counters. The feedback-on minus feedback-off differences were +93.15, +43.99, +86.75, +73.08, and +57.34 successful query pairs per CPU-second (mean +70.86; exact sign test two-sided p=0.0625). Run order was always off then on, so time/order effects remain possible. This is not an equal-CPU allocation experiment, bug-yield result, or evidence of distinct bugs. Independent parser and per-arm raw metadata: `results/sqlancerpp_feedback_cpu_4121_4125/independent_analysis.json`.

## Literature evidence update (not a new discovery)

- Batch 34's two previously identifier-less citation-follow-up papers now have downloaded, hash-verified official PMLR full texts. The 2023 active-membership-inference paper reports attacks under its explicitly malicious-server threat model and studied LDP mechanisms; it sharpens the threat-model/measurement gap for finding 157, but does not refute LDP universally. The 2013 arXiv crowdsourcing paper is officially withdrawn and unavailable as a PDF, so its old abstract claim is excluded. See `docs/fulltext_audit_batch34.md` and `reports/fulltext_batch_recovery.json`.

This file is intentionally sparse. Only verified raw experiment outputs can add new empirical discoveries; literature-derived claims remain labeled as such.

## DP158 numerical reproduction and corrected negative lead

- **Source-matched scalar Figure 12 simulation (exploratory, not a new breakthrough):** Using the paper's explicit small-`q` budget formula at `q=0.1`, an independent million-path-per-arm implementation obtained P/Q halt rates **0.988712 / 0.987891** versus the published **0.9886 / 0.9880**; mean active steps **113.136 / 113.149** versus **113.1**. PLRV moments and empirical Gaussian-CDF discrepancies are recorded in `results/dp158_filter_source_matched_q01/independent_analysis.json`. The first exact-KL preregistration was withdrawn after source review; this run is explicitly exploratory. It does not verify a theorem, establish a new privacy bound, or audit deployed code.
- **Retracted interpretation:** A previous 100,000-path-per-arm dimension sweep looked material, but it modeled a hypothetical vector output with exact one-step KL. Appendix G.2 writes `y_i²` without clarifying scalar output versus vector shorthand, and the paper explicitly defines a different approximate `Budg`. Thus this sweep is **not** evidence of an omitted output dimension or a paper reproducibility gap. The raw results and correction remain in `results/dp158_filter_dimension_sensitivity/summary.json` and `research/experiment_preregistration_dp158_dimension_sensitivity.md` for auditability.
- A valid fully adaptive fixed-order RDP-filter theorem is available as a baseline, but no production implementation or matched accountant comparison has yet been pinned. The current status and source links are in `reports/dp158_accountant_audit.json`.
