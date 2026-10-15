# SQLancer/SQLite feasibility check (2026-10-13)

This is an execution and instrumentation check for the first CS direction
dossier, not a bug-discovery result or a matched-budget effect estimate.

## Pinned inputs

- SQLancer source: `sqlancer/sqlancer` commit
  `d8e6b158a1a18ab803d1c90bbbc45f58c94c60ba` (MIT license).
- Built JAR SHA-256:
  `3c8f75d54ab1e9fca7a37946b12ef8618c0a6adb829118043614b81c8643501c`.
- Build/runtime image:
  `maven@sha256:99e61abcff91a9b1333463bd8451fb18495d6eba9250ac66a338b518f8278320`.
- Actual SQLite version in SQLancer's JDBC log: **3.49.1**. The host SQLite
  CLI is 3.51.0 and was not the tested engine.
- Common oracle: `NoREC`; one thread, seed 4101, one try, one generated
  database, 200-query cap, 30-second process limit, isolated network,
  one CPU and 1 GiB memory per condition.
- Reproduction command: build that pinned checkout with
  `docker run --rm --mount type=bind,source=CHECKOUT,target=/work --workdir /work maven:3.9-eclipse-temurin-21 mvn -q -DskipTests package`,
  then run `python3.12 scripts/run_sqlancer_feasibility.py --sqlancer-source CHECKOUT --output NEW_OUTPUT_DIRECTORY`.
  `CHECKOUT` must be replaced with an absolute path to the pinned source.

## Observed output

| Condition | Exit | Oracle queries | Databases | Wall time | Other trace |
| --- | ---: | ---: | ---: | ---: | --- |
| Unguided SQLancer | 0 | 195 | 1 | 2.059 s | 605 successful / 25 unsuccessful statements |
| Query-plan guidance | 0 | 200 | 1 | 2.199 s | 848 successful / 28 unsuccessful statements; 200 plan-log rows, 32 unique row strings |

The exact machine metadata and raw SQLancer output are in
`results/sqlancer_feasibility_v2/metadata.json` and the two condition
directories. Both conditions used the same JDBC SQLite version and NoREC
oracle. The QPG plan log confirms the guidance code path was selected.
The plan-log count is an internal trace only: baseline plan signatures
were not logged, so it is not a comparative plan-coverage result.

The first attempt is retained at `results/sqlancer_feasibility/`.
It set `--max-generated-databases 1` but left SQLancer's default
`--num-tries 100`, creating many databases within its time limit.
The revised runner pins `--num-tries 1`; only the v2 outputs above are
the one-database feasibility pair.

## Decision and remaining evidence

The common-oracle SQLancer versus QPG pair is executable on this host
using Docker. This removes the local Java installation blocker.
It does **not** establish a QPG effect on bug discovery: there is one
seed, two short runs, slightly different completed query counts, no
independent root-cause triage, and no confirmed new bug. It also does
not test SQLancer++ validity feedback or SQLaser clause guidance.

The source audit found that SQLancer++'s general provider cannot combine
its validity feedback with QPG as a flag-only 2×2 design; it also pins a
different SQLite JDBC version. See `docs/sqlancerpp_compatibility_audit.md`.
The multi-seed work therefore treats each tool as a separate within-tool
ablation and never pools their raw bug counts.
