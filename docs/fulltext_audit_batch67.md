# Full-text audit batch 67: multi-agent coordination, 2015–2019

This batch completes the lexical-priority arm for `agent_memory_coordination × 2015–2019`. The sampled papers address different goals—privacy-preserving planning, correlated cooperation, and fair resource allocation—so their scores are not directly comparable.

## Sampled full texts

### 1. Best-First Width Search for Multi Agent Privacy-Preserving Planning (`1906.03955v1`)

MA-BFWS combines novelty-based width exploration with goal-directed heuristics in distributed MA-STRIPS planning. The evaluation uses 3,404 single-goal benchmark instances and 16 domains, plus CoDMAP/MBS multi-agent planning benchmarks on a 512-node InfiniBand cluster. It reports that `2-MA-BFWS` solves 91.63% of the single-goal instances under its width criterion, versus 96.94% for the hFF comparison; results depend substantially on domain and heuristic. Five runs are used for the nondeterministic distributed benchmarks, with medians reported.

The privacy mechanism is not equivalent to hiding all information: true private facts can be represented to other agents by a shared dummy identifier. The paper explicitly says others can infer that a private fact exists and monitor its truth value, and may infer private actions/causal effects. It compares exchanged information with other planners and describes its own privacy as stronger in this protocol sense, while leaving fully protected black-box models and privacy effects of novelty pruning for future work.

### 2. Signal Instructed Coordination in Cooperative Multi-agent Reinforcement Learning (`1909.04224v2`)

SIC gives all agents a shared random coordination signal at the start of an episode and trains local policies to condition on it, with information-theoretic regularization. The paper formalizes how a common signal can expand decentralized joint policies toward the centralized policy space under its assumptions. Empirically it tests matrix games and 2-vs-2/4-vs-4 predator–prey environments; predator–prey comparisons use 10 random seeds and report stable gains for the tested SIC integrations.

**Boundary:** the signal is common to all agents and state-independent within the episode; the experiments do not test lossy/unavailable signals or deployed communication. The theory does not remove the operational need to distribute the signal or establish that every task benefits.

### 3. Learning Fairness in Multi-Agent Systems (`1910.14472v1`)

FEN combines a fair-efficient reward with a controller and specialized sub-policies. Its paper proves Pareto-efficiency/fairness properties under optimal-policy assumptions and evaluates three designed environments: job scheduling, a “Matthew effect” resource game, and a manufacturing-plant game. It reports five random-seed runs per scenario. In job scheduling, FEN reaches 90% resource utilization with CV 0.17, while independent agents reach 96% utilization with CV 1.57; here fairness improves at a modest utilization cost. In the Matthew-effect and manufacturing scenarios, the paper reports that FEN improves both fairness and its scenario-specific efficiency metric relative to the tested baselines.

**Boundary:** these are small constructed environments and a particular fairness measure/reward design; five seeds are not evidence of deployment generality. The paper itself notes that hyperparameters can substantially affect performance.

## Synthesis: keep privacy, coordination, and fairness as separate axes

Across these three papers, “better multi-agent behavior” depends on what is measured and assumed. Masking fact names still permits some truth-value inference; shared signals can enlarge a policy class only when all agents receive/use the signal; and fairness–efficiency effects vary by scenario and metric. A bounded next experiment is a common multi-agent resource-allocation suite with a declared threat model and tunable signal loss: compare centralized, decentralized, signal-conditioned, and privacy-preserving planners while reporting (a) reward/throughput, (b) per-agent minimum utility and inequality, (c) messages/bytes, and (d) inference-based privacy leakage. Vary agent count, heterogeneous goals, and adversarially correlated observations. The proposed synthesis weakens if improvements remain stable across these axes and held-out tasks without extra leakage, communication, or fairness loss.

This is a research lead from the sampled papers, not a novelty claim or a claim that any of the papers is invalid. Their benchmarks, methods, and outcomes are not pooled into a single effect estimate.

## Primary sources

- https://arxiv.org/abs/1906.03955
- https://ojs.aaai.org/index.php/ICAPS/article/view/3472
- https://arxiv.org/abs/1909.04224
- https://doi.org/10.1007/978-3-030-94662-3_12
- https://arxiv.org/abs/1910.14472
- https://proceedings.neurips.cc/paper/2019/hash/10493aa88605cad5ab4752b04a63d172-Abstract.html
