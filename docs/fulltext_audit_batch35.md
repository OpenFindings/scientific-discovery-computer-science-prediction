# Full-text audit batch 35: agent reliability depends on the kind of failure

Updated 2026-10-12. This advances the fixed uniform-random `agent_reliability_security` cell. Three sampled papers were read in full across 2012, 2023, and 2026; a fourth 2010 sample was metadata/abstract-checked but its arXiv full text could not be retrieved. A cited 2026 memory benchmark was read as independent follow-up evidence. This batch is neither a completed audit of the eight unread keys in this cell nor a prevalence estimate.

## Sampled papers

### 1. A Trust Model Based on Service Classification in Mobile Services (arXiv:1011.3096v1; 2010)

[arXiv metadata and abstract](https://arxiv.org/abs/1011.3096); [conference record](https://doi.org/10.1109/GreenCom-CPSCom.2010.19).

The abstract describes an intermediary trust/billing operator, service sensitivity classes, high/medium/low trust bands, and authentication histories/penalties. The arXiv PDF/HTML could not be retrieved here; I therefore do not count this as a full-text audit or make a claim about its numerical evaluation. Metadata identifies the related 2010 GreenCom/CPSCom proceedings paper. The indexed full-text snippet mentions threshold comparisons, but that is not enough to validate the experimental design or results.

### 2. Decentralized Multi-agent Plan Repair in Dynamic Environments (arXiv:1202.2773v1; AAMAS 2012 full version)

[Exact full text](https://arxiv.org/html/1202.2773).

This paper gives a useful positive result with unusually explicit boundaries. In a three-agent logistics simulation with action failures, two plan-repair methods use 59% and 43% of the replanning baseline's messages on average. But the same study finds the gain declines in loosely coordinated rover/satellite domains and disappears under one kind of randomized state perturbation; the authors say large perturbations can favor replanning. The implementation limits evaluation to plans with at most two coordination landmarks, and the experiments are simulated planning domains rather than physical multi-robot deployments. The paper itself formulates a stronger average-complexity hypothesis as future work; it validates a narrower hypothesis about communication in selected conditions.

### 3. A Picture is Worth a Thousand Words: Language Models Plan from Pixels (EMNLP 2023; arXiv:2303.09031v1)

[Published full text](https://aclanthology.org/2023.emnlp-main.1025.pdf).

The VP2 approach directly conditions a language model on visual observations. It reports better success than the compared baselines on VizALF and VirtualHome; for example, the paper's table reports 55.3/27.8% on VizALF ID/OD and 20.6/7.5% on VirtualHome ID/OD. Two qualifications change how to read that result: the environments are simulators, and 64 of 187 in-distribution plus 52 of 190 out-of-distribution ALFWorld evaluation tasks were impossible because of low-level action implementation bugs. The authors normalize success by an oracle agent's success rate and explicitly say the scenarios are less complex than the real world. This is positive benchmark evidence for visual grounding, not evidence of real-robot reliability.

### 4. FlowState: Execution State as Memory for Long-Horizon LLM Agents (arXiv:2609.34565v2; 2026)

[Exact full text](https://arxiv.org/html/2609.34565v2).

FlowState stores typed execution-state nodes with links to tool observations, updates them incrementally, and retrieves prior state progressively. In the paper's MemoryArena experiments it improves task-success/progress metrics and reports 43.2% fewer tokens than full-context use with the same DeepSeek-V4-Flash model. The results are not uniformly positive on every endpoint: on the Retail portion of tau³-Bench, task pass/database accuracy improve while action accuracy falls by 4.9 percentage points. Results across three base models are encouraging, but memory-system/state-tracking baselines are compared primarily with one base model; the paper says full source code will be released later. Its own ethics section explicitly says benchmark results do not establish safety for deployment and flags sensitive retained data and stale or incorrect assumptions as real risks.

## Independent follow-up: STALE tests the risk FlowState itself flags

### STALE: Can LLM Agents Know When Their Memories Are No Longer Valid? (arXiv:2605.06527v1; 2026)

[Exact full text](https://arxiv.org/html/2605.06527v1); [author code and benchmark repository](https://github.com/icedreamc/STALE).

STALE evaluates 400 expert-validated implicit-conflict scenarios (1,200 queries) with separate tests for state resolution, resistance to questions that assume an outdated fact, and downstream policy adaptation. Even Gemini-3.1-pro reaches only 55.2% overall, and its State Resolution score for one conflict type is 92% while Premise Resistance is only 30%—recognizing a stale fact does not mean the system will refuse to act on a query that assumes it. The paper validates its automatic judge on 240 responses, reporting 95.83% agreement with human labels (Cohen's κ=0.9152). Its limitations are also material: conflicts are controlled, one-shot old/new pairs; scenarios are LLM-generated then expert-validated; such data may not match organic longitudinal interactions. Its CUPMem prototype lifts its benchmark score, but that is not an external replication or live-user validation.

This is direct counterevidence to a simplistic “better memory just improves agents” story. FlowState's state representation can improve selected benchmark task outcomes and token use; STALE shows that retaining/updating information is not enough unless the system adjudicates whether old state remains valid and whether the new state controls downstream action. The two papers measure complementary axes, not competing results on one shared benchmark.

## Bounded synthesis and next test

The sampled evidence is highly conditional. Plan repair saves messages in tight coordination, but not under every domain/failure regime. Visual planning improves simulator success, while benchmark action bugs remove many nominal evaluation tasks. Explicit state memory improves selected multi-session outcomes and efficiency, while stale-state tests expose substantial downstream reasoning failures. These are three different mechanisms and three different failure modes; “agent reliability” is too broad to serve as one outcome.

**Falsifiable follow-up:** Re-run a common set of multi-session tool tasks with explicit injected state changes, stale-premise user queries, tool/action failures, and communication/token budgets. Compare full-context, retrieved memory, explicit state tracking, and state adjudication; report task completion, unsafe/stale action rate, recovery after environment/tool failure, context/communication cost, and results on held-out scenarios. The opportunity weakens if existing independent evaluations already measure these endpoints jointly on matched tasks and demonstrate reliable transfer beyond simulation.

The 2010 trust-model sample remains abstract-only in this audit. The reliability/security topic still has additional unread random keys and requires further work before any broader synthesis.
