# Research recovery audit

**Audited:** 2026-10-13 UTC. This distinguishes files present in the local worktree from files in Git history and from remote objects actually read from R2.

## Available state and recovery

- Git has only `main` and `origin/main`, both at `e3cd133` when audited; no alternate branch contained a newer recovery copy. The pushed commit contains literature audit batches 76 and 77. The worktree had 43 tracked files and 321 dirty/untracked status entries at audit start, much of it the substantial research corpus and results. Do not blanket-stage this tree.
- Batch audit reports and review ledgers for 8, 15, 30, and 34 existed locally but were untracked and absent from Git history. Their review-ledger row counts are respectively 7, 4, 6, and 9; batch 34 has only 7 rows with an arXiv ID (two rows lack one). The actual reports must be versioned selectively if they are to survive a fresh checkout; no evidence was recreated from memory.
- The full arXiv CS metadata corpus is present locally: 937,531 records from the export API. A lexical screen matched 198,690 unique records for candidate topics. A stratified frame contains 407 distinct arXiv papers (428 topic-period rows), with uniform-random and lexical-priority arms, three selections per cell. These are screening/frame sizes, not a complete scientific review or estimates of topic prevalence.
- `data/research_candidates_uncapped.jsonl.gz` (profile: 198,690 matched papers) and the 1.6-GB `data/arxiv_cs_corpus.jsonl` are local; the latter is intentionally ignored by Git. The metadata/candidate corpora are not backed up in the Git commit and must not be mistaken for remotely archived evidence.
- Full-text acquisition: 139 manifest attempts = 120 downloaded + 19 failed. Every one of the 120 downloaded PDFs exists locally and matches its recorded SHA-256; all 120 have extracted text and extraction records. The local tree contains 120 PDFs and 120 text files. The 19 failures have not been repaired in this audit.
- R2: using the authenticated Wrangler OAuth session, explicitly in `--remote` mode, every one of the 122 original object keys in `data/fulltext_r2_upload_manifest.jsonl` was read back and verified against receipt bytes and SHA-256 (**122/122 passed**). After recovery, 24 additional objects were uploaded to a new, non-colliding prefix and independently read back (**24/24 byte and SHA-256 checks passed**). The combined manifests contain 146 object keys; the two duplicate keys remain in the original set. Temporary readback copies were removed. See `reports/r2_recovered_batches_remote_verification.json` and its manifest.
- Batch recovery: the four review ledgers contain 26 rows (7/4/6/9). Twenty-five rows now have locally present, SHA-verified full text; 24 PDFs were newly recovered (22 from public arXiv and two from official PMLR proceedings), and one was already present. The 2013 arXiv:1311.5417 row remains unavailable: the official record marks it withdrawn, provides no PDF, and states there is no license for the withdrawn version. We did not bypass that restriction. Batch coverage is 7/7, 4/4, 6/6 and 8/9. Recovery details and per-file hashes are in `reports/fulltext_batch_recovery.json`.
- External source checkouts used in earlier DBMS runs are available in `/private/tmp` at audit time, including SQLancer++ commit `1405d4eb5b7af7a639717a47147bd89362558830`. `/private/tmp` is ephemeral and is not a durable source archive; experiment metadata pins commit and image digest. Docker daemon access is restricted in the sandbox unless separately authorized.

## What has actually run

- Four-case Paper 5 executor/falsification pilot: hand-written synthetic snippets, infrastructure smoke test only. It is not a real benchmark and says nothing about scientific-agent effectiveness.
- Real pinned SQLite/NoREC feasibility and operational studies exist, including 10-seed short within-tool comparisons and five SQLancer++ pairs at 20 databases. In the short SQLancer++ study, feedback on/off had identical operational counts/traces in all 10 pairs. The longer exploratory study has five complete pairs and feedback-on minus feedback-off derived successful-query-pair differences `+215, +221, +373, +277, +244`. Its logger retained per-database rates rather than exact raw denominators; these are operational proxies, not matched CPU-hour bug yields. Some SQLancer short runs did not complete a database. No distinct logic bug is confirmed. Full details: `docs/dbms_guidance_campaign.md` and linked `results/` JSON/logs.
- Fresh-seed replication: preregistered seeds 4111–4115 completed 5/5 with exact reconstructed query-pair counts. Feedback-on minus feedback-off differences were +265, +346, +407, +265, +299; two-sided exact sign test p=0.0625. This measures an operational query-generation proxy only.
- CPU-normalized follow-up: preregistered seeds 4121–4125 completed 5/5 with cgroup-v2 `cpu.stat` `usage_usec` counters captured inside each container. Feedback-on minus feedback-off successful-query-pair throughput differences were +93.15, +43.99, +86.75, +73.08, and +57.34 pairs per CPU-second; mean +70.86, median +73.08; two-sided exact sign test p=0.0625. Run order was fixed (off then on), so order/time effects are not excluded. This is still a narrow operational proxy, not bug yield or a randomized matched-budget effectiveness test. See `results/sqlancerpp_feedback_cpu_4121_4125/independent_analysis.json`.

## Findings 155–158 and evidence tier

These are literature-derived leads (not independent discoveries, validated forecasts, or new theorems):

| Finding | Evidence actually recorded | Main boundary / next test |
|---|---|---|
| 155 code review order | Prior controlled evidence is defect-class-specific; a newer field study uses a post-review fix proxy. | Instrument actual inspection and randomized file order in a consenting review setting; independently adjudicate defects. |
| 156 supply-chain controls | Developer-reported usability/adoption and workflow/security-failure descriptions are not verified intervention outcomes. | Link time-stamped adoption to independently verified incidents with denominators and a causal design. |
| 157 dependence-aware LDP | Private dependence tests, directed LDP leakage analysis, and distribution-shift caveats are distinct established threads. Full-text counterevidence also includes an actively malicious server achieving high membership-inference success under the specific LDP mechanisms and settings studied in ICML 2023; this is not a universal LDP refutation. | Separate central-DP screening from LDP release; compose guarantees; compare attacks, utility and shift on multi-attribute data and explicitly include active-server attacks. |
| 158 adaptive DP filters | Approximate privacy filters have validity regimes; the reported concern is not proof that production accountants generally underestimate. | Pin theorem/code, test heterogeneous sequences and boundary regimes against high-precision accounting plus valid conservative baselines. |

Each source/counterevidence chain is recorded in `data/research_findings_batch76.jsonl`, `data/research_findings_batch77.jsonl`, and corresponding audit reports. Broad novelty claims in 155 and 157 were explicitly rejected/bounded.

## Paper 3 / Paper 4 status

- Paper 3: methodology and astronomy baseline are documented in `docs/paper3_methodology.md`; the astronomy dataset/results are not locally archived here. `data/research_questions.jsonl` contains 26 source-linked candidate CS questions (derived from 29 arXiv records), all with a single cutoff date around collection time, not historical snapshots and matured future labels. Thus no leakage-free historical CS outcome forecast has been validated.
- Paper 4: its offline evidence-graph/action-ranking method is documented in `docs/paper4_methodology.md`, but this repository has not yet established action-level outcomes that could validate expected utility. There is no completed adaptive scientific-agent comparison.

## Proceed now

1. The two predeclared operational query-proxy seed blocks are complete. Keep distinct bug yield unmeasured and do not call the throughput result matched-CPU effectiveness.
2. Archive the small missing batch reports, ledgers, findings, and follow-ups into Git without committing raw PDFs or the large ignored corpora.
3. The 25 retrievable audit-batch full texts are now recovered and hash-verified; one withdrawn arXiv record remains unavailable by design. Both source-linked PMLR rows now have official full texts.
4. Next, randomize arm order in a preregistered CPU-matched test and independently deduplicate/reproduce any NoREC discrepancies before making bug-finding claims.
5. Continue Paper 3 historical-snapshot/outcome collection and Paper 4 action-outcome validation; neither methodology has yet transferred successfully.

## Recovery limitations

The untracked corpus and many earlier audit batches are recoverable only from this worktree/local storage or external public sources, not from the current Git branch. R2 contains verified copies of the 120 original full texts plus the 24 recovered full texts, not the entire 937k arXiv corpus. Do not commit raw PDFs or treat an upload manifest as proof absent a successful remote GET/hash comparison. The withdrawn 2013 record has no usable PDF and remains a documented exception.
