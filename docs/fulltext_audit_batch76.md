# Full-text audit batch 76 — software supply chain, 2025–2026

## Scope

This closes the frozen six-version cell `software_supply_chain × 2025–2026-through-10-11`: three lexical-priority papers newly read here and three uniform-random records already audited in batches 8 and 30. New reads cover Sigstore adoption, AI developer-reported security issues, and file order in code review. “Software supply chain” is the frozen sampling label; the file-order paper is adjacent evidence about review as a security/quality control, not direct supply-chain-attack measurement.

The new exact-version PDFs total 2,822,725 bytes / 65 pages. Three new reads and three reconciliations are recorded in `data/fulltext_review_ledger_batch76.jsonl`.

## New full-text reads

### Why Johnny Adopts Identity-Based Software Signing: A Usability Case Study of Sigstore (2503.00271v6)

This is a qualitative study of 17 experienced practitioners, recruited through professional networks; interviews took place November 2023–February 2024. The authors report saturation around interview 12, but the sample is expert- and Sigstore-network-biased, and participant 18 was excluded from analysis. Interviewees described lower key-management friction and easier CI/CD signing, while also reporting integration gaps, enterprise/regulatory constraints, transparency-log privacy concerns, rate/latency issues, and poor fit for offline/air-gapped environments. This is useful evidence about adoption mechanisms and usability barriers. It does not measure deployment-wide adoption rates, malicious-artifact prevalence, or whether signing reduced compromises.

### Securing the AI Supply Chain: What Can We Learn From Developer-Reported Security Issues and Solutions of AI Projects? (2512.23385v2)

The January 9, 2026 v2 (the paper says accepted to ICSE 2026) retains the abstract's pipeline and headline counts: a keyword-plus-classifier pipeline yields 312,868 predicted/retrieved security discussions, and thematic coding of 753 posts yields 32 issue and 24 solution categories across system/software, external tools/ecosystem, model, and data. The version history shows v1 on Dec. 29, 2025 and v2 on Jan. 9, 2026; comparing the frozen v2 with the v1 arXiv record shows the abstract-level result is unchanged. This is a map of developer-reported discussions, not an estimate of real-world issue prevalence or causal mitigation effectiveness. Its 753-post stratified sample supports taxonomy discovery; do not read category counts as incident rates. The classifier's manually labeled training/validation corpus is 723 discussions, while a separate test set is only 100 keyword-free discussions (18 positive); the overall MCC of 0.79 therefore does not itself validate every one of the 312,868 inferred records. Human thematic coding used consensus/debriefing, not a reported independent reliability coefficient for every post.

### Does Order Matter? An Empirical Investigation into the Impact of File Ordering on Code Review Effectiveness (2609.22610v1)

The paper mines 330,343 multi-file merged pull requests / 756,814 file instances from 182 GitHub projects and five languages. Only 406,266 of 939,011 retrieved merged PRs had reviewers; single-file PRs are excluded. “Latent bug” is an explicit proxy: a file is counted when it appears in a bug-fixing PR immediately after a prior modification. Manual validation of 384 bug-fix/non-bug-fix commit messages reports Cohen's κ=.97, but that validates the commit-message classifier, not whether the later fix was caused by the earlier PR or review. The paper says this proxy can include an older defect, later requirement, or maintenance change.

Later positions have higher proxy-label rates (56.7% at position 1 to 61.5% at position 30), but the association is small (reported Pearson r=.022, Spearman ρ=.018; Cramér's V=.062). The dataset is observational, default path order is not actual inspection sequence, and file complexity/churn/coupling are not fully controlled. Comment activity is also an imperfect attention measure: proxy-labeled files get more comments, but comments need not mean semantic inspection or successful detection. These findings are not causal evidence that alphabetical order creates defects.

## Reconciled random arm

Three exact versions were previously audited and are reconciled without counting new reads:

- `2512.23480v1`, “Agentic AI for Autonomous Defense…” (batch 8), reports >90% autonomous mitigation and <6% overhead. The reviewed paper lacks the repository/sample inventory, denominators, splits, uncertainty, and linked code/data needed for independent reproduction. This is limited auditability, not proof that the claim is false.
- `2602.14572v3`, “An Empirical Study of the Evolution of GitHub Actions Workflows” (batch 30), studies 267,955 histories across 49,258 active public repositories. More precise permissions and pinning are configuration changes, not proof of prevented incidents; its before/after LLM-era analysis is observational and inconclusive.
- `2608.26831v1`, “When Relationships Break…” (batch 30), reports benchmark IDS performance on CIC-IDS-2018 and CIC-UNSW-NB15, including up to 7× lower inference time in reported scenarios. These pre-collected datasets do not establish performance under real-network shift or reduced analyst/incident outcomes.

## Findings and falsifiable leads

### Finding 155 — Bridge code-review position experiments to field defect outcomes

The question “does file position affect review?” is not new. Fregnan et al. studied 219,476 PRs and ran a controlled experiment with 106 participants: placing one seeded defect type last rather than first reduced its detection odds by 64%, while a second defect type showed no position effect. The new 2026 field study adds scale (330,343 PRs) and a modest later-position association in a post-review bug-fix proxy, but cannot causally attribute a given defect to a given review. Taken together, they suggest a narrower, testable lead: identify which defect classes and contexts transport the controlled position effect into real PRs, and validate comments/default order against actual per-file inspection and independently adjudicated defects. This is not a claim that file-order effects are undiscovered.

**Test:** In consenting repositories, randomize file order (or use a stepped rollout) and instrument actual viewed files/time. Stratify seeded or independently adjudicated defects by type, file complexity, coupling, churn, PR size, and reviewer experience. Pre-register defect-detection sensitivity and review time; then link field outcomes to later fixes without treating every later bug-fix commit as a missed defect. The lead weakens if position has no reproducible defect-class-specific effect after randomized exposure or if comment/default-position proxies closely track actual inspection and detection.

### Finding 156 — Keep adoption and policy signals separate from security outcomes

Across this cell, signing usability, developer issue reports, workflow hardening, anomaly scores, and autonomous mitigation are different stages of evidence. The Sigstore interviews explain why organizations may adopt or reject signing, but do not measure breach reduction. The AI taxonomy maps reports but is not an incident-rate sample. The workflow study measures configuration evolution, while the autonomous-defense paper reports strong mitigation numbers with insufficient detail for independent audit. A useful study would connect adoption and policy changes to verified artifact integrity, exploitability/reachability, and observed incident outcomes, while preserving denominators and deployment context. This is a measurement/validation lead, not evidence that the tools do not work.

**Test:** Follow a set of repositories before/after verifiable signing or automated remediation adoption; record signed-artifact coverage, key/identity failures, confirmed malicious or vulnerable artifact reachability, remediation latency, and incidents per release/deployment. Use a matched or randomized rollout with a pre-registered threat model and public artifact bundle. The lead weakens if adoption/configuration metrics reliably predict independently confirmed security outcomes across ecosystems and deployment settings.

## Limitations

One fixed six-version cell, only three newly read PDFs. It is not representative of the 198,690-paper candidate pool and does not yield field prevalence or a global novelty claim. The targeted comparator search for file ordering is strong enough to reject a broad novelty claim, but is not a systematic review of the full code-review literature. The Sigstore paper is qualitative and temporally bounded; the AI paper relies on platform discussions and a classifier; the file-order study is observational and proxy-dependent. Findings remain research leads requiring systematic follow-up.
