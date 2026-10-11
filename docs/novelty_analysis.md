# Novelty and transfer analysis

## Verified versus proposed

Verified from the supplied request: Paper 4 is described as an offline planner with typed evidence graphs, hypotheses, provenance, evidence gaps, candidate actions, expected information gain, novelty, tractability, cost, Bayesian updating, and historical evaluation; it explicitly does not execute experiments. These are user-provided descriptions, not independently audited source facts.

Implemented here as new infrastructure: safe execution, deterministic evidence interpretation, persistent research memory, an executable pilot, and tests that preserve raw observations.

Not yet verified: Paper 4's exact utility weights, seven metric definitions, astronomy benchmark schema, updater assumptions, repositories, and Paper 3-informed transfer weights.

## Contribution boundary

The defensible Paper 5 contribution is the evaluated transition from offline action ranking to constrained, provenance-preserving execution and feedback. Combining an LLM with a planner alone is not a novelty claim. The final comparison must establish whether execution and feedback improve objective resolution under matched budgets and must report negative transfer if Paper 4 assumptions do not generalize.

