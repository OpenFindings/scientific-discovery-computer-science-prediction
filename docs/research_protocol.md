# Research protocol (Paper 5 pilot)

## Scope

The first campaign targets software-engineering causal diagnosis in controlled, executable failures. This tests infrastructure and measurement validity; it is not evidence that the method solves SWE-bench or performs scientific discovery in the broad sense.

## Pre-specified pilot

- Benchmark: `controlled-pilot-v1`, four cases, two competing hypotheses.
- Primary outcome: exact causal-mechanism resolution.
- Secondary outcomes: action count, declared action cost, and belief entropy after each observation.
- Planner: expected entropy reduction plus tractability minus cost.
- Stopping rule: at most two actions; choose the highest-ranked remaining action.
- Truth access: only the benchmark harness may access the hidden truth; agents receive observations from executed actions.
- Repetition: deterministic replay first; stochastic model comparisons require a frozen model/configuration and repeated seeds before claims are made.

The protocol intentionally excludes confidence intervals and significance claims for four pilot cases. Those belong to the final evaluation after benchmark validation and pre-registration.

## Safety and validity

Only allow-listed programs may execute, shell interpretation is disabled, timeouts are recorded, and stdout/stderr/exit status are retained. Failed or timed-out experiments are first-class records. The pilot's oracle-backed observation adapter is a test fixture, not a production experiment executor.

