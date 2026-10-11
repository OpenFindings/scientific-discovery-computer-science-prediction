# Research protocol (Paper 5 execution and falsification pilot)

## Scope

The first campaign targets software-engineering causal diagnosis in controlled, executable failures. This tests infrastructure and measurement validity; it is not evidence that the method solves SWE-bench or performs scientific discovery in the broad sense.

## Pre-specified executable comparison

- Study: `P5-EXEC-FALSIFY-PILOT-001`, benchmark `controlled-executable-diagnosis-v1`.
- Cases: four runnable code fixtures covering a null guard fault, an indexing fault, a third mechanism, and a context-dependent confound.
- Competing hypotheses: null guard, boundary indexing, and none of the above.
- Conditions: direct fixed probe; fixed workflow; one-step Paper 4 utility adapter; utility adapter with posterior feedback; and utility adapter followed by an explicit counter-hypothesis probe.
- Primary outcome: correct resolved diagnoses divided by all four cases.
- Resolution rule: posterior at least 0.80 after at least two distinct probe families.
- Secondary outcomes: unsupported provisional conclusions, action count/cost, and counterevidence events.
- Budget: maximum three actions per case and identical registered probes for every condition.
- Planner weights: Paper 4 default configuration, IG 10, novelty 1, tractability 1, cost 1. Novelty uses an explicit unseen-provenance-root adapter and is recorded separately.
- Likelihoods: declared in `execution_study.py`; Bayesian updates assume conditional independence between probe outcomes. All probes operate on the same case artifact, so this assumption is a known limitation and not equivalent to independent source provenance.
- Truth access: task source and question are passed to the policy; hidden labels are read only by the scoring block after the policy returns.
- Repetition: one deterministic run per system/question cell. The result is a software plumbing pilot, not a powered comparison.

With four cases, Wilson intervals are shown descriptively and no significance claim is made. The originally separate `controlled-pilot-v1` remains a deterministic unit fixture and is not mixed into this comparison.

## Safety and validity

Only Python commands are allow-listed, shell interpretation is disabled, and each action has a temporary workspace, timeout, CPU/memory/file/output limits, a scrubbed environment, and raw stdout/stderr/exit status in the record. macOS `sandbox-exec` restricts reads to the task, system, and Python runtime paths, denies network, and permits writes only in the action scratch directory. In this managed Codex run, nested `sandbox-exec` was denied, so the pilot used the outer managed sandbox with process resource limits; the report records this backend. The managed-sandbox fallback is opt-in and the command-line runner enables it only with `--managed-outer-sandbox`.

Failed and timed-out experiments remain first-class records. Before evaluating a real public benchmark, the executor must be run in a supported OS/container sandbox and the benchmark's license, dependencies, and task-level leakage risks must be audited.
