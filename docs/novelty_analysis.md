# Novelty and transfer analysis

## Verified versus proposed

Verified from the supplied repositories: Paper 3 is a temporally split astronomy outcome-prediction study with 980 questions and structured evidence-context features. Paper 4 is an offline planner with typed evidence graphs, hypotheses, provenance, evidence gaps, candidate actions, expected information gain, provenance-based novelty, tractability, cost, Bayesian updating, and seven historical-evaluation metrics; it explicitly does not execute experiments.

Implemented here as new infrastructure: safe execution, deterministic evidence interpretation, persistent research memory, an executable pilot, and tests that preserve raw observations.

Not yet imported into this worktree: Paper 4's exact utility estimators, seven metric implementations, astronomy benchmark schema, updater assumptions, and Paper 3-informed transfer configuration. The source repository does expose these artifacts and should be pinned as an input for the next implementation stage.

## Contribution boundary

The defensible Paper 5 contribution is the evaluated transition from offline action ranking to constrained, provenance-preserving execution and feedback. Combining an LLM with a planner alone is not a novelty claim. The final comparison must establish whether execution and feedback improve objective resolution under matched budgets and must report negative transfer if Paper 4 assumptions do not generalize.
