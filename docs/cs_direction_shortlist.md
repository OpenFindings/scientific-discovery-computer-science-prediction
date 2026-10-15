# CS research directions: source-backed decision dossiers

Generated from `data/direction_decisions.json` and source-located records in
`data/research_findings*.jsonl`. These are decisions to run the next
check, not validated Paper 3 forecasts or claims of global novelty.
Paper 3 has no CS historical labels or calibrated model in this worktree;
Paper 4's action values have not been validated on these questions.
The source-method audit is in `docs/paper3_paper4_source_audit.md`.

## dbms-guidance-comparison

**Stage:** real within-tool proxy runs completed; integrated 2×2 incompatible; bug-yield question remains open.

**Question:** Under matched DBMS versions, test oracles, CPU-hour budgets, hardware, seed policy, and blinded vendor-confirmed root-cause deduplication, do validity feedback, query-plan novelty, and historical clause/call-chain targeting each increase confirmed unique logic-bug yield, and are their effects complementary?

**Why test it:** Three source-audited methods optimize different guidance signals. Real within-tool tests show proxy behavior worth probing, but the key uncertainty is whether those gains correspond to distinct, reproducible logic bugs at equal cost.

**Measured outcome:** Vendor-confirmed root-cause-distinct logic bugs per CPU-hour; time to first confirmed unique logic bug.

**Observed feasibility:** On 10 short SQLancer seeds, 9/10 database pairs completed and QPG made 7.33 more NoREC checks on average; seed 4109 completed no database despite exit 0. SQLancer++ feedback on/off was indistinguishable for 10 three-database seeds, but a 20-database follow-up had more rate-derived successful query pairs with feedback on in all five tested seeds (+215,+221,+373,+277,+244). These are proxy outcomes, not confirmed bug yield. See docs/dbms_guidance_campaign.md.

**Competing explanations:**

- Validity feedback raises executable SQL yield, but plan guidance adds no distinct logic bugs at matched cost.
- Plan guidance reaches distinct bug behaviors beyond the gain from valid SQL alone.
- Apparent cross-paper bug-yield differences arise mainly from DBMS, oracle, budget, and deduplication choices.

**Source trail:**

- [Testing Database Engines via Query Plan Guidance](https://arxiv.org/html/2312.17510): §V-Q.2, Tables V and Figure 3: 10-run, 24-hour plan coverage; TiDB/CockroachDB stopped at 6 hours after crashes.
- [Scaling Automated Database System Testing](https://arxiv.org/html/2503.21424): §5.3, Table 5: CrateDB TLP feedback ablation, 1 hour × 5 runs; 11.4 vs 9.8 average unique bugs.
- [SQLaser: Detecting DBMS Logic Bugs with Clause-Guided Fuzzing](https://arxiv.org/html/2407.04294): §3: 144 historical bugs analyzed into 35 clause patterns.

**Next action:** Pre-register an equal-CPU-hour bug-yield and behavior-coverage phase. Keep the SQLancer/QPG and SQLancer++ feedback studies separate. Freeze a repeated-seed, equal-CPU-hour budget; log exact per-database valid SQL and plan/behavior signatures. Independently reproduce and root-cause-deduplicate any NoREC discrepancy, including zero-discovery runs. Compare each toggle only with its own pinned baseline.

**Budget rule:** Use a small preregistered gate before any full agent campaign; stop or redesign if setup failures or missing exact counters prevent interpretation.

**Action is informative if:** A proxy gain survives matched CPU cost and reaches distinct reproducible behaviors or logic bugs.

**Evidence against the working explanation:** The proxy gain disappears at equal CPU cost or produces no additional distinct behavior after independent triage.

**Prerequisite:** The integrated 2×2 design is incompatible in the released code; see docs/sqlancerpp_compatibility_audit.md.

**Stop rule:** Stop any cross-method effect or interaction claim until a common implementation, DBMS revision, oracle, and budget are validated.

**Evidence record:** `data/research_findings.jsonl`. Source independence,
artifact compatibility, and global novelty remain to be checked.

## agent-tool-outcome-gap

**Stage:** benchmark and artifact audit.

**Question:** On matched tasks with a fixed model, tool set, and call/token budget, does explicit stagewise tool routing, schema feedback, and evidence integration improve end-to-end task correctness beyond merely increasing valid calls, especially for multi-source tasks?

**Why test it:** Two source-audited agent benchmarks report a gap between valid tool calls and task success. The actionable uncertainty is which stage loses information under a fixed tool and token budget.

**Measured outcome:** End-to-end exact/task success; secondary outcomes separately score tool selection, schema-valid invocation, retrieved-evidence relevance, and evidence-supported final answer.

**Competing explanations:**

- Selecting the wrong tool or route explains a substantial share of failed tasks.
- The main loss occurs after valid tool calls, when the agent integrates evidence and forms an answer.
- The apparent gap is substantially driven by benchmark grading or task composition.

**Source trail:**

- [MCP-Radar: A Multi-Domain Benchmark for Assessing Tool-Use Capabilities of Large Language Models](https://arxiv.org/html/2505.16700): §5 / Table 3: valid-call and final-accuracy gap, including file-management result.
- [InfoMosaic-Bench: Evaluating Tool-Augmented LLMs Across Domains](https://arxiv.org/html/2510.02271): §§5.2–5.3: domain variation from tool augmentation and 22.4% tool-selection/use error category.

**Next action:** Instrument matched tasks and replay oracle tool routes. Pin a public task subset, a single model, tool inventory, and call/token limits. Log routing, schema validity, evidence returned, evidence use, and final answer. Replay a valid oracle route with the same answer procedure and budget to estimate how much route choice explains the failure.

**Budget rule:** Begin with 20 auditable multi-source tasks; set the larger sample after checking task and grading reproducibility.

**Action is informative if:** Oracle-route replay raises final task success on previously failed cases without changing evidence or token budget.

**Evidence against the working explanation:** Final task success remains low after route correction, pointing to evidence integration or answer verification instead.

**Prerequisite:** Verify benchmark task files, license, grading code, and availability of reproducible tool responses.

**Stop rule:** Do not claim a routing intervention if the benchmark cannot separate tool choice from evidence use or if oracle replay changes the information budget.

**Evidence record:** `data/research_findings_batch3.jsonl`. Source independence,
artifact compatibility, and global novelty remain to be checked.

## code-uncertainty-equivalence

**Stage:** artifact and cost audit.

**Question:** On repository-level code repair and code translation, does symbolic equivalence improve uncertainty calibration and selective risk enough to justify execution cost and bounded-checker error, across project sizes and unseen repositories?

**Why test it:** The reviewed studies disagree in ways consistent with their different program-equivalence checks. Repository-scale behavior and timeout-related misclassification remain directly testable.

**Measured outcome:** Risk-coverage curves and calibration for human-verified correctness, including false acceptance, unnecessary abstention, checker timeout, and compute cost.

**Competing explanations:**

- Bounded symbolic equivalence improves uncertainty calibration after accounting for checker cost and error.
- Short-program benchmark structure or checker timeouts explain the apparent advantage.
- Model, sampling, and correctness-oracle differences explain more of the cross-study contrast than the equivalence method.

**Source trail:**

- [Look Before You Leap: An Exploratory Study of Uncertainty Analysis for Large Language Models](https://arxiv.org/html/2307.10236): §§V-A–V-D: model/task heterogeneous AUC results.
- [Assessing Correctness in LLM-Based Code Generation via Uncertainty Estimation](https://arxiv.org/html/2502.11620): §4 and Table 2: clustering-specific correlation results.

**Next action:** Audit equivalence-checker errors on a held-out repair set. Pin the released checker and a repository-held-out code-repair set. Compare embedding, CodeBLEU, and bounded symbolic equivalence on the same generated candidate patches. Independently adjudicate a stratified set of checker agreements, disagreements, and timeouts before any risk-coverage claim.

**Budget rule:** First measure checker timeouts and reviewer effort on a small frozen sample; set a full matched compute budget from that pilot.

**Action is informative if:** Symbolic clustering improves calibrated selective risk after including checker runtime and false-equivalence errors.

**Evidence against the working explanation:** Timeout or false-equivalence rates erase the risk-coverage gain, or the gain does not transfer beyond the original short-program benchmark.

**Prerequisite:** Audit released implementations, candidate-sampling protocol, repository benchmark license, and independent correctness labels.

**Stop rule:** Defer an effectiveness claim if equivalence errors cannot be independently measured or repository-level correctness has only weak test oracles.

**Evidence record:** `data/research_findings.jsonl`. Source independence,
artifact compatibility, and global novelty remain to be checked.
