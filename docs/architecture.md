# Research architecture

Paper 5 uses two connected paths. The question-level transfer runner is protocol-only until an audited registry exists. The executable agent comparison follows:

`ResearchQuestion -> candidate action planner -> registered probe -> constrained executor -> raw observation -> deterministic outcome parser -> declared-likelihood Bayesian update -> replayable JSON trace`

`ResearchAgent` exposes a pluggable model-policy interface for action selection and a separate falsification decision. The policy returns only registered action IDs. The runtime resolves those IDs to fixed command templates; raw model-generated shell commands are rejected before execution.

The executable pilot compares direct selection, fixed workflow, a Paper 4 utility adapter, feedback updating, and active falsification. It uses four runnable code cases, including an explicit context-confound case. The planner never receives the hidden answer key; scoring occurs after each policy returns.

Facts, hypotheses, observations, and interpretations have separate types. The execution trace retains actual stdout/stderr and parsed outcomes. All probes within a case share the same subject artifact, so Bayesian conditional independence remains a pilot assumption rather than proven source independence.

## Executor boundary

`SafeExecutor` rejects non-allow-listed executables, shell use, and working directories outside the declared action root. On macOS it applies a sandbox profile with network denial and scratch-only writes plus process resource limits. This host's managed sandbox denied nested `sandbox-exec`, so the recorded run used the inherited outer managed sandbox fallback. Other platforms fail closed until an OS sandbox backend is added.

## Variants

The Paper 4 condition uses the verified default weights from `configs/default.yaml` (IG 10, novelty 1, tractability 1, cost 1) and records each utility component. Its novelty estimator is a provenance-root adapter, not a byte-for-byte import of the reference implementation. The five conditions in the synthetic pilot are deterministic policies, not LLM agents.
