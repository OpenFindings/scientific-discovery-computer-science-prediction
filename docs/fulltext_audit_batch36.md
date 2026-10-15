# Full-text audit batch 36: proposal, proof, simulation, and field evidence are different things

Updated 2026-10-12. This batch closes the four remaining unread uniform-random keys in the current `agent_reliability_security` topic-period cells. All four sampled papers were checked against full text. A peer-reviewed 2023 systematic review was also traced as an independent landscape-level countercheck, but only its publisher record/abstract was available in the web session; it is not counted as a full-text follow-up. Together with batch 35, eight of twelve random keys in this topic have now been reviewed or dispositioned; four remain.

## Four remaining sampled papers

### 1. Opinions within Media, Power and Gossip (arXiv:1102.2336v1; 2011)

[Exact full text](https://arxiv.org/pdf/1102.2336).

This is a simulation study motivated by Italian political-media data, not an experiment that estimates the causal effect of media on real voters. Its baseline uses 100 agents, 100 simulation turns, and ten repetitions per parameter setting; media reach and agent tolerance are varied. The simulated effect is nonlinear: at low tolerance, peer-to-peer discussion partly inhibits the media signal; at tolerance 0.5, when broadcast reaches more than 70% of agents, peer discussion amplifies the model's media message. A separate “white zone” scenario—agents reached by neither experts nor media—can change the pattern again. Experts are treated as truthful in the model, while media messages are deliberately fixed to favor one issue. So the useful result is conditional behavior of this model, not evidence that peer discussion generally protects the public from misinformation.

### 2. Contribution to the Formal Specification and Verification of a Multi-Agent Robotic System (arXiv:1604.05577v1; 2015)

[Exact full text](https://arxiv.org/pdf/1604.05577).

The paper formally checks safety/liveness properties for a storehouse stock-transport case study and maps specifications through an architecture to a C# robotics simulation. It reports a finite system: two carrier agents, nine road partitions, collision/deadlock constraints, and a stock-conservation property. This is meaningful model-level evidence—formal verification is stronger than simply showing a few successful runs—but it is still a simulation/model-checking case, not a physical robot deployment. The authors list automated model transformation/code generation and graphical tooling as future work, so the verified-property-to-deployed-code path is not fully established by this paper. The proof also depends on the chosen finite model and stated requirements being adequate representations of the intended system.

### 3. Personal Universes: A Solution to the Multi-Agent Value Alignment Problem (arXiv:1901.01851v1; 2019)

[Exact full text](https://arxiv.org/pdf/1901.01851).

This is a conceptual proposal, not a tested alignment method. It suggests personalized simulated worlds as an alternative to merging everyone's values into one shared system. Crucially, it explicitly assumes that extracting each person's values will already have been solved and says evaluating value-extraction methods is outside scope. It also discusses unresolved issues such as how to measure whether a person's values are being served and possible psychological consequences of simulated life. It should be recorded as a proposal and its assumptions, not counted as empirical evidence that value alignment works.

### 4. Multi-Agent Optimization for Safety Analysis of Cyber-Physical Systems: Position Paper (arXiv:2403.16904v1; 2024)

[Exact full text](https://arxiv.org/html/2403.16904).

The authors propose using adaptive multi-agent optimization to select preventive actions after FMECA. The paper is unusually explicit that this is preliminary: its initial model covers only a cost constraint and two of four action/failure relationship types; time constraints and more realistic coverage remain future work. It further says the existing FMECA tools do not yet provide the information needed to realize its proposed solution directly, including constraints and automated calculation of residual safety criticality. There is no reported end-to-end benchmark or real CPS evaluation in this position paper. The claimed opportunity is therefore a design direction awaiting operationalization, not an evaluated safety improvement.

## Independent countercheck: the wider validation literature already recognizes this evidence gap

### Testing, Validation, and Verification of Robotic and Autonomous Systems: A Systematic Review (ACM TOSEM 2023)

[Peer-reviewed publisher record and abstract](https://doi.org/10.1145/3542945).

The systematic review reports screening more than 10,000 studies and coding 192 included papers. Its abstract says many studies lack rigorous efficiency/effectiveness/adequacy measures, and that evidence of industrial applicability and consolidated benchmarks remain limited. This is useful counterevidence to any claim that the current sample alone discovered a new validation gap: the wider robotics V&V literature has already named closely related problems. The full publisher text was not accessible in this session, so this is abstract-level corroboration only, not a full-text audit. It also covers robotic/autonomous systems broadly rather than exactly the sampled agent-reliability label.

## What changed in the synthesis

Across the current sampled cell, the papers make different kinds of claims: simulated social dynamics, model-checked properties under a finite robot model, a normative value-alignment proposal, and a preliminary safety-optimization architecture. They cannot be ranked on a common “agent reliability” metric. A bounded, non-novelty-claim opportunity is to test the evidence chain itself: whether specifications match the intended environment, whether implementations preserve verified properties, and whether tested outcomes transfer to physical or operational settings. The broader systematic review means this is an established research challenge, not an unclaimed discovery; the useful contribution here is to turn it into a targeted, falsifiable comparison across sampled agent-system papers.

**Falsifiable follow-up:** For representative agent/robot safety systems, preregister a chain of checks: stakeholder requirement adequacy; formal property verification on a model; model-to-code trace/refinement conformance; simulated fault injection; and physical or operational tests. Report which assurance claim each stage supports, failure coverage, residual counterexamples, runtime/cost, and field transfer. The narrower gap is weakened if prior studies already test this complete chain with shared outcomes across multiple systems and show reliable model-to-deployment transfer.

The twelve-paper topic cell is still not fully closed: four random keys remain unread, and the topic's papers span simulation, formal methods, value-alignment theory, planning, and memory systems. No prevalence inference is warranted.
