# SQLancer++ compatibility audit for the DBMS-guidance question

Source: [SQLancer++](https://github.com/suyZhong/SQLancerPlusPlus), pinned at `1405d4eb5b7af7a639717a47147bd89362558830` (source inspection, 2026-10-13). Repository `LICENSE.md` permits reuse under MIT terms. Comparator: official [SQLancer](https://github.com/sqlancer/sqlancer), pinned at `d8e6b158a1a18ab803d1c90bbbc45f58c94c60ba`; the bounded SQLite/NoREC run is recorded in [sqlancer_feasibility.md](sqlancer_feasibility.md).

## Can the two guidance mechanisms share a 2×2 experiment?

No, not by toggling the published code's flags. In SQLancer++, `src/sqlancer/general/GeneralOptions.java` defines `--enable-feedback` for the `general` provider and includes a NoREC oracle. But `GeneralProvider` does not override the query-plan-guidance methods in `src/sqlancer/ProviderAdapter.java`: `initializeWeightedAverageReward`, `getQueryPlan`, and `executeMutator` each throw `UnsupportedOperationException` by default. The global `--qpg-enable` flag routes execution to this path in `src/sqlancer/Main.java`. The `general` provider therefore cannot simply run its validity feedback and QPG together. The original SQLancer SQLite provider supports QPG, but does not incorporate SQLancer++'s general validity-feedback generator. Within SQLancer++, `--enable-feedback false` gates generator-option updates after successful database runs; other learning toggles remain separate, so a feedback on/off contrast must state exactly what was disabled.

There is a second comparability issue: SQLancer++ pins `sqlite-jdbc` 3.40.0.0 in `pom.xml`; the tested SQLancer build used JDBC SQLite 3.49.1. Same DBMS *name* and NoREC oracle do not establish a common target or generation semantics. A direct bug-count comparison across these builds would be confounded.

## Decision

Do **not** present a four-cell validity-feedback × plan-guidance study or claim SQLancer++ versus QPG effectiveness. Two distinct, narrower tests remain scientifically useful: (1) a within-SQLancer unguided/QPG comparison at matched seeds and CPU budget; (2) a within-SQLancer++ feedback on/off comparison with its own frozen SQLite/NoREC setup. The independent experiments can test whether each guidance proxy changes valid-query yield and behavioral coverage, but cannot identify a cross-method interaction without a new, validated common implementation. Bugs require independent reproduction and deduplication.

This is a falsification result about the *proposed experimental design*, not evidence that either method lacks merit.

## Bounded execution check

The pinned SQLancer++ JAR was built in the existing Docker Maven/JDK image; no host Java installation was needed. `scripts/run_sqlancerpp_feasibility.py` mounted the repository's `dbconfigs` read-only, disabled networking and LLM learning, capped each condition at one CPU/1 GiB, three databases, and 200 NoREC queries per database. The final one-seed run is `results/sqlancerpp_feasibility_v3/metadata.json` with raw logs alongside it. Both feedback-off and feedback-on exited 0 on JDBC SQLite **3.40.0**, each reporting 3 databases, 438 oracle queries, 649 successful and 194 unsuccessful statements. Those equal totals do not imply equivalence: one seed and a short cap are not an effect estimate, and the feedback flag only gates one generator-option update path. The on-condition generated a larger option-statistics CSV even though aggregate counts were unchanged. A repeated-seed operational check is recorded separately in `results/dbms_guidance_campaign_v3/`.
