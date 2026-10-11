# Research progress

Updated 2026-10-11.

## Completed

- Created typed question, hypothesis, action, evidence, graph, execution, interpretation, Bayesian-update, planning, and memory modules.
- Added a deterministic controlled pilot benchmark and reproducibility tests.
- Added safety checks for shell-free allow-listed execution and timeouts.
- Added initial Paper 5 protocol, architecture, registry, and reproducibility documentation.
- Executed `controlled-pilot-v1`: 4/4 cases resolved (1.000 exact resolution rate); this is a deterministic infrastructure pilot, not a final comparative result.

## Source audit status

The user supplied the Paper 3 and Paper 4 repositories. Their public GitHub pages were audited; verified methodology, implementation boundaries, benchmark metrics, and Paper 4 revision caveats are recorded in `docs/foundational_audit.md`. The repositories are not vendored into this worktree, so their code has not yet been imported directly.

## Blockers and next steps

The final Paper 5 study requires pinned local checkouts of the Paper 3/4 repositories, a licensed benchmark subset, a frozen model/tool budget, and independent evaluation. Papers 6 and 7 have not been run and must not receive results claims.
