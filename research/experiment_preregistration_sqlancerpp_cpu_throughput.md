# Preregistration: CPU-normalized SQLancer++ feedback throughput

- **Study ID:** `EXP-DBMS-FEEDBACK-CPU-THROUGHPUT-4121-4125`
- **Registered:** 2026-10-13 UTC, before running seeds 4121–4125.
- **Motivation:** The fresh seeds 4111–4115 replicated a higher successful-query count under identical caps, but did not measure container CPU time. This study adds an independent cgroup CPU counter.
- **Question:** Under the same pinned SQLancer++/SQLite 3.40.0/NoREC setup and fixed 20-database × 200-attempt caps, does feedback-on yield more successful query pairs per container CPU-second on five unused paired seeds?
- **H0:** Feedback-on does not show consistently greater query-pair throughput per CPU-second on the five paired seeds.
- **H1:** Feedback-on has a positive within-seed throughput difference on all five seeds.
- **Primary outcome:** Per seed, `successful query pairs / cgroup-v2 usage_usec`, converted to CPU seconds, for each arm; compare the on-minus-off rate. The rate numerator is reconstructed from the pinned source's direct `(double) qsuccess / queryNum` output and denominator 200.
- **Seeds and controls:** 4121–4125; same commit, JAR SHA, container image digest, database version, oracle, query/database caps, one CPU, and network disabled. Seed pairing is retained. No cross-tool comparisons.
- **Resource accounting:** Capture `/sys/fs/cgroup/cpu.stat` `usage_usec` from inside each container to a mounted result file before container exit. Wall time and throttling counters are secondary checks, not substituted for CPU time. If any complete pair lacks a valid counter, report measurement failure and do not infer normalized effect.
- **Analysis:** Preserve all per-database rates and container CPU stats. Report five paired numerator/rate pairs, mean/median/range, sign count, and exact sign test (two-sided and directional). No exclusions except incomplete pairs specified before outcomes; no optional stopping.
- **Interpretation gate:** Even a positive throughput result is a narrow operational proxy, not distinct bugs per CPU hour. If positive, the next milestone remains exact bug deduplication/reproduction under blinded triage; if null/negative, down-rank the direction.
- **Reproduction command:** `python3.12 scripts/run_sqlancerpp_long_campaign.py --source /private/tmp/sqlancerpp-source-1405d4e --output results/sqlancerpp_feedback_cpu_4121_4125 --first-seed 4121 --seeds 5 --database-cap 20`, followed by `scripts/analyze_sqlancerpp_cpu_campaign.py`.
