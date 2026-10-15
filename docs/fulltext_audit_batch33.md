# Full-text audit batch 33: one “multi-agent” label, incompatible kinds of evidence

Updated 2026-10-12. This completes the six unread uniform-random records in the `agent_memory_coordination` topic-period cells. It is a fixed-frame audit, not a systematic review or a prevalence estimate.

## Six records checked against their full texts

### 1. Communication-Free Multi-Agent Control under Local Temporal Tasks and Relative-Distance Constraints (arXiv:1410.8673v1; 2014)

[Exact full text](https://arxiv.org/html/1410.8673v1).

This is a formal control paper, not a benchmark study. It proves task satisfaction and preservation of a connected sensing graph for agents following local LTL tasks, under its stated controller and mathematical assumptions. Those assumptions matter: agents are two-dimensional single-integrator point masses, so collisions are explicitly not modeled; all agents share a sensing radius; the initial neighbor graph must be connected; and task regions are separated. The evidence is a theorem plus computer simulations, not a physical-robot collision or communication-failure test. “Communication-free” means the controller uses relative state measurements of neighbors, not that agents require no sensing or shared local observations.

### 2. Evoplex: A platform for agent-based modeling on networks (arXiv:1811.10116v2; SoftwareX 2019)

[Published full text](https://www.matjazperc.com/publications/SoftwareX_9_199.pdf).

This is research software for running graph-based agent simulations, not evidence that an agent policy solves coordination tasks better. The article describes a flexible experiment/visualization interface and a multithreaded engine. Its illustrative prisoner’s-dilemma run uses a 99×99 grid for up to 1,000 steps but only one trial; that demonstrates the software workflow, not statistical validation of a scientific hypothesis. The authors position the platform for parameter sweeps and large-scale simulation, but the paper does not provide a common, independently reproduced head-to-head performance benchmark against current simulators. This is a tooling contribution; do not pool it with control success rates.

### 3. Collision Detection for Agents in Multi-Agent Pathfinding (arXiv:1908.09707v3; 2019)

[Exact full text](https://arxiv.org/html/1908.09707v3).

This technical report organizes collision-detection methods and derives exact collision intervals for specified shapes and motion models. Its most useful warning is about error direction: coarse bounding volumes can generate false positives and waste feasible paths; sparse trajectory sampling can miss a real collision, a false negative that can make a path infeasible or unsafe. The derivations are scoped to modeled geometry and motion (including constant velocity and selected constant-acceleration cases), and the report explicitly leaves exact unsafe intervals for accelerating agents as future work. It is an analytical methods report, not a broad empirical deployment comparison.

### 4. Energy Management of Multi-mode Hybrid Electric Vehicles based on Hand-shaking Multi-agent Learning (arXiv:2209.02633v3; 2022)

[Exact versioned full text](https://arxiv.org/pdf/2209.02633v3).

The paper compares two DDPG agents with a single-agent controller in a MATLAB/Simulink software-in-the-loop PHEV model. Across three initial battery charge settings, the multi-agent system reports 2.13–2.55% lower fuel use and lower state-of-charge error; an independence ratio of 0.2 is selected from the tested ratios. This is a real quantitative comparison, but it is simulation on a constructed driving cycle assembled from four standard cycles, not road testing or fleet evidence. The authors themselves say the ratio needs tuning: poorly chosen coordination can make the learners move in opposing directions or both deteriorate. Thus this supports a bounded simulated control result, not a general claim that adding agents saves energy.

### 5. A Large Language Model-based multi-agent manufacturing system for intelligent shopfloor (arXiv:2405.16887v2; 2024)

[Exact versioned full text](https://arxiv.org/pdf/2405.16887v2).

Unlike the preceding simulation papers, this work reports deployment on a physical intelligent shopfloor. Its selected outcome is makespan, and the LLM-Hunyuan configuration is strong in the reported test: for FIFO/FILO/SPT workpiece selection the table reports 583/609/633 seconds, versus 690/743/714 for Random. But the result is highly conditional. Removing the reference answer raises Hunyuan makespan to 990/993/1,022 seconds—worse than Random—and GLM-4-Flash also performs worse than the best heuristic in several cases. The experiment is repeated five times, but the reported central outcome is still makespan on this shopfloor rather than a broad physical safety/quality endpoint. Across 49,437 API calls, 11 errors are reported, mostly network errors with retry; the authors note ambiguous decisions can be referred to a human. The architecture sends data to external closed-source LLM APIs and explicitly says public APIs should be used only where data-security requirements are low. The authors’ own conclusion points to locally deployed models as future work. This is valuable physical evidence, but model, prompt/reference-answer protocol, latency, human fallback, and data exposure are part of the result—not incidental implementation details.

### 6. S5-SHB Agent: Society 5.0 Enabled Multi-Model Agentic Blockchain Framework for Smart Home (arXiv:2603.05027v2; 2026)

[Exact full text](https://arxiv.org/html/2603.05027v2). The paper labels itself a preprint, not peer-reviewed.

The headline “99–100% decision acceptance” is not a demonstrated rate of correct or safe real-home actions. The multi-agent evaluation uses eight sessions across four Gemini variants and two conditions, each over 30 decision cycles in a simulated 16-device household; the paper reports the 3,916 decisions accepted, but its threat schedule is fixed. Its own limitations say simulation-only evaluation, one LLM provider, fixed threats, and one household. Blockchain measurements are also simulated/configuration-specific. There is an important tradeoff: the balanced adaptive configuration reports 15.2 ms emergency response, 478 ms overall block latency and 15.9 tx/s; the aggressive configuration reports 5.4 ms emergency response but 4,642 ms overall latency and 1.5 tx/s. The discussion elsewhere gives different emergency figures (6.8 ms and 3.0 ms for C and D), an internal reporting inconsistency that should be resolved before reusing the headline latency claim. This paper is a promising prototype, but acceptance/confidence, safe action, physical deployment, and throughput under household load are distinct outcomes.

## What this audit says—and does not say

These six items share a retrieval label, not one estimand. They represent at least five different evidence types: formal guarantees under assumptions, simulation tooling, analytical collision methods, model-based control simulation, physical shopfloor evaluation, and simulated LLM/blockchain governance. Their outcomes—LTL satisfaction, collision false negatives, fuel use, makespan, decision acceptance, latency, and throughput—cannot be compared or combined into a single “multi-agent performance over time” curve.

The actionable cross-cutting issue is narrower: papers often report the system’s local success measure (theorem satisfaction under a model, simulated fuel, shopfloor makespan, or accepted decisions) without that measure alone establishing the downstream property a reader may infer (physical collision avoidance, road fuel savings, manufacturing safety/quality, or safe home actuation). This is a hypothesis for the larger audit, not yet a field-wide conclusion.

**Falsifiable follow-up:** Reclassify the remaining random and lexical-priority records into evidence type, deployment level, primary outcome, and whether the claimed outcome is independently ground-truthed. The hypothesis predicts the broad “multi-agent” aggregate trend will be unstable or uninterpretable until stratified by those variables. It is weakened if the same well-defined endpoint and deployment level recur across a substantial, representative portion of the uncapped candidate pool and yield a consistent trend under a preregistered analysis.

## Sampling update

This batch audits all six previously unread random-frame keys for `agent_memory_coordination`, raising that topic’s random arm from 6/12 to 12/12. It adds six papers but only closes one topic’s random arm; it does not exhaust the 18-topic frame or turn the larger candidate corpus into a full-text review.

## Retrospective check against the other six random records in this topic

The other half of this fixed random draw had already been audited in batches 6, 8, and 14. It adds important counterevidence to any overly simple “the field just has mismatched metrics” summary:

- The 2013-labeled LP-DPOP paper, TeamReg/CoachReg MARL, and PAC value-factorization paper each report genuine gains in particular constraint regimes or benchmark tasks, but also document clear reversals, weak cases, or limits on cross-version/baseline comparison. TeamReg, for example, is strong on SPREAD/BOUNCE but substantially below MADDPG on adversarial COMPROMISE. The independent 25-task MARL benchmark cited in batch 14 likewise reports that algorithm rankings depend on observability, reward sparsity, and environment family; it is useful counterevidence to a universal algorithm ranking, not a replication of TeamReg or PAC.
- MHGPO, a more recent LLM multi-agent search system, reports a large HotpotQA F1 gain (21.45 to 50.86 in one reported comparison) but tests a fixed three-agent pipeline on static multi-hop QA, not open-ended research or long-horizon tool use. This is positive evidence that a clearly scoped coordination problem can improve, while still not licensing transfer to a different task class.
- GitHarness is a genuine retrieval false positive: it tests one assistant tracking a person’s changing requirements, not coordination among multiple autonomous agents. It must be excluded from claims about agent-agent coordination even though it passed the broad topic screen.

Across the complete 12-paper random draw, the defensible candidate finding is therefore not “coordination methods do not work.” It is: method rankings and claimed gains are conditional on task structure, objective, observability/reward setup, model/prompt protocol, and evidence type; broad topic-level aggregation can reverse or erase the signal. The six newly audited papers add a separate deployment/endpoint distinction (formal or simulated outcome versus real-world property), while the six earlier papers show conditional wins and benchmark-specific counterexamples. Those two patterns should be measured separately, not collapsed into one explanation.

**Stronger falsifiable study:** On the remaining sampled coordination papers, preregister a coding scheme for (a) task family and incentive structure, (b) observability and reward regime, (c) agent roles/parameter sharing, (d) simulation versus physical deployment, (e) primary endpoint and its ground truth, and (f) matched baseline/tuning/seed budget. Then test whether method rank changes are predicted by those moderators on held-out task families, with per-task results and negative effects reported. The hypothesis weakens if one method remains superior across those held-out strata under equal tuning and compute, and if deployment-grounded endpoints agree with the benchmark proxy. This design directly accommodates positive evidence such as MHGPO and the specialized MARL results instead of assuming away their successes.

## Independent follow-up: smart-home evaluation has advanced, but still leaves a sim-to-physical gap

I searched for independent later work rather than treating S5-SHB Agent as the whole evidence base. Three relevant sources sharpen—and partially challenge—the candidate gap:

### SimuHome (arXiv:2509.24282v3)

[Exact version-3 full text](https://arxiv.org/html/2509.24282v3).

This is a substantial counterexample to the claim that later work only counts tool calls or accepted text. SimuHome runs agents in a Matter-protocol-based smart-home simulator and checks final device/environment state. Its manually validated benchmark has 600 episodes; the version-3 paper evaluates 18 LLMs. Explicit device-control tasks can recover from an initial invalid call using tool feedback (over 40% of successful QT3 episodes did so), whereas workflow scheduling remains difficult and agents often fail to detect their own scheduling errors. This is stronger state-grounded evidence than a decision-acceptance counter, but it is still simulation, not a longitudinal physical-home trial. The paper's deployment aspirations should not be mistaken for a hardware evaluation.

### SMH-Bench (arXiv:2606.01912v1)

[Exact full text](https://arxiv.org/html/2606.01912v1).

This independent benchmark broadens coverage to 1,100 human-audited tasks, 7 categories, 22 subcategories, and simulated homes up to 135 devices. It evaluates 13 LLMs in direct-reasoning and environment-interactive settings, and checks actual state transitions in HomeEnv. Top models exceed 85% on some results, but the authors report substantial inconsistency as complexity increases and persistent weaknesses in ambiguous intent, automation/scheduling, personalization, and multi-device composition. This is important positive methodological counterevidence: environment-grounded final-state verification is feasible and is now being applied at scale. But HomeEnv remains a simulator; the paper's front matter says data and code are “coming soon,” which limits immediate independent reproduction.

### Evil-AI Benchmark (IEEE Access 2026; DOI 10.1109/ACCESS.2026.3727159)

[Peer-reviewed publication record and abstract](https://researchportal.tuni.fi/en/publications/evil-ai-benchmark-an-evaluation-framework-for-adversarial-securit/).

This is a narrower physical-world counterexample: it reports five adversarial threat classes, 350 scenarios across five smart-environment domains, and an Arduino-driven servo to physically verify actuator-trigger events. Reported attack success varies substantially across eight LLMs (0.8%–54%), so tool invocation or average acceptance is plainly not a safety guarantee. However, the full-text PDF was denied to this session (HTTP 403); I have therefore checked the peer-reviewed publication record/abstract only and do not count it as a full-text audit. A small servo verifies that an actuator event occurred, not that a complete deployed home remained safe over time.

### Updated interpretation

The original candidate gap was too broad if phrased as “papers do not measure downstream outcomes.” SimuHome and SMH-Bench already verify environment state in simulation, and Evil-AI reports limited physical actuator verification. The narrower, better-supported opportunity is to test how well these increasingly strong simulated and component-level measures predict end-to-end physical safety and task success under changing states, delayed/failed devices, adversarial inputs, and extended operation. The evidence here is mixed in a useful way: benchmark design is improving; reliable scheduling, complexity scaling, adversarial robustness, and end-to-end physical validation remain open in the audited sources. A new systematic/full-text search is needed before any priority or novelty claim.
