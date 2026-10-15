# Paper 5 research protocol: execution and falsification

## Status and correction

The four-case `controlled-executable-diagnosis-v1` run is an infrastructure
smoke test only. Its cases are hand-authored synthetic Python snippets. It is
not the Paper 5 evaluation, does not use an external research benchmark, and
cannot support claims about AI research agents or real software defects. Keep
it only for regression-testing the executor, evidence log, and scoring code.

The primary empirical domain is being reset to database-system logic-bug
testing, based on the source-level comparison in
[`research_finding_dbms_fuzzing.md`](research_finding_dbms_fuzzing.md). This
choice is grounded in full-text review of QPG, SQLancer++, and SQLaser, which
report different guidance signals and incompatible budgets/outcomes. The
literature supports a comparability gap, not a claim that any of the methods
are ineffective or that combining them is novel.

## Revised research question

Under matched DBMS version, oracle, and compute budget, can an execution-capable
research agent select and run evidence-acquisition actions, update its belief
about which guidance signal is useful, and deliberately probe for counter-
evidence more reliably than (a) unguided SQLancer, (b) a fixed test workflow,
and (c) offline Paper 4-style action ranking without observation-driven
replanning?

The concrete signals motivated by the reviewed papers are:

1. SQL-validity feedback (SQLancer++);
2. query-plan diversity feedback (QPG / SQLancer guidance); and
3. historical logic-bug clause-pattern guidance (SQLaser).

These are candidate experimental actions, not yet implemented as one agent.
SQLancer and SQLancer++ source commits and licenses have now been audited.
Their released code cannot simply be combined into a validity-feedback × QPG
factorial experiment: SQLancer++'s general provider lacks QPG hooks and pins
a different SQLite JDBC version. SQLaser integration remains unaudited. See
[`sqlancerpp_compatibility_audit.md`](sqlancerpp_compatibility_audit.md).

## Planned effectiveness study (not yet run)

- **Initial target:** SQLite with NoREC, but compare guidance toggles only
  *within the same pinned tool/build*. Do not pool SQLancer and SQLancer++
  results while their SQLite revisions and generators differ.
- **Conditions:** unguided versus QPG within SQLancer; feedback off versus on
  within SQLancer++; then, only if a common implementation is built and
  validated, feasible combinations, fixed workflow, offline action selection, feedback/replanning;
  and feedback plus an explicit falsification step that spends budget trying
  to contradict the leading hypothesis about which signal helps.
- **Fairness:** same DBMS build, oracle, CPU-hours, hardware, concurrency,
  timeout policy, seed list, restart accounting, and bug deduplication rules.
  Randomize run order and use repeated independent seeds. Do not compare raw
  bug counts copied from papers with different budgets.
- **Primary outcome:** independently reproducible, root-cause-distinct logic
  bugs per CPU-hour. Maintainer confirmation/fix status is reported separately
  and cannot be assumed for untriaged findings.
- **Secondary outcomes:** executable-input rate, plan-signature diversity,
  coverage, unique reproducer count, time to first reproducible finding,
  resource cost, oracle disagreement, and cases where counterevidence changes
  the agent's selected action or conclusion.
- **Falsification requirement:** register the leading mechanism claim before
  the challenge run; preserve the original reproducer and raw trace; then run a
  predeclared probe that would be unlikely under that claim. A failed challenge
  is not itself proof of the alternative. Correlated probes must not be treated
  as independent evidence in Bayesian updates.
- **Analysis:** report per-engine and per-seed outcomes, uncertainty intervals,
  zero-discovery runs, failures, and all exclusions. Do not infer that proxy
  improvements (validity, coverage, or plan novelty) imply more real bugs.

## Entry criteria before a real run

1. Pin and audit the three source repositories and relevant benchmark/artifact
   revisions; document license and reproduction instructions.
2. Prove that the selected conditions can share the same DBMS version and
   oracle, or narrow the study rather than silently changing conditions.
3. Implement a harness dry-run on an actual DBMS build and verify CPU-time,
   seed, crash, restart, and raw-evidence accounting.
4. Freeze benchmark, hypotheses, endpoint, deduplication/triage protocol,
   exclusions, stopping rule, and analysis before opening outcome labels.
5. Run the repeated matched-budget experiment and inspect every result before
   drafting empirical claims.

## Current execution status and interpretation

Docker provides Java/Maven; the user does **not** need to install Java on the
host. A pinned, no-network SQLancer/SQLite 3.49.1/NoREC unguided–QPG pair ran
to completion (`sqlancer_feasibility.md`). A pinned SQLancer++/SQLite
3.40.0/NoREC feedback-off–on pair also ran to completion
(`sqlancerpp_compatibility_audit.md`). These are feasibility runs, not
evidence of differential bug discovery. The cross-tool 2×2 design was
falsified by the source audit. There is no confirmed new logic bug, and no
claim of agent-level scientific effectiveness yet. The four synthetic cases
remain a regression smoke test only.

A subsequent 10-seed short-run campaign and five-seed longer SQLancer++
feedback check are reported in `dbms_guidance_campaign.md`. They supply a
real operational proxy result and a cautionary zero-database run, but still
no matched-CPU bug-yield or agent-effectiveness result.
