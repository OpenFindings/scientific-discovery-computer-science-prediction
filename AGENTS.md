# Research mission

Read `research/state.json`, `RESEARCH_STATUS.md`, and `research/task_queue.json` at the start of every session. Continue the highest-priority eligible research task without asking the user to restate context.

Use Paper 3 as described in `docs/paper3_methodology.md` for leakage-free, point-in-time forecasts with temporal validation. Use Paper 4 as described in `docs/paper4_methodology.md` to structure competing hypotheses, provenance-linked evidence gaps, candidate experiments, and explicit costs/information-gain assumptions. Planning scores are not proof of scientific value.

Keep literature observations, leads, novelty-bounded hypotheses, historical forecasts, executed experiments, and independent validation as separate evidence levels. Preserve null, negative, and failed outcomes. Never fabricate sources, use future information in historical predictions, infer causal effects from proxy labels, or present synthetic data as observations. Do not publish papers or change production OpenFindings.

The repository map is: `data/` source data/manifests; `docs/` methods/audits; `scripts/` reproducible tools; `results/` immutable outputs; `research/state.json` checkpoint; `research/task_queue.json` scheduler; `research/experiment_ledger.jsonl` append-only outcomes; `RESEARCH_STATUS.md` current summary; `reports/` evidence-tiered synthesis. Do not commit restricted full-text PDFs, licensed corpora, credentials, or unrelated pre-existing changes.

Research loop: discover → structure → forecast → plan → execute → falsify → update → rerank → continue. Re-evaluate findings 155–158, but do not favor them over stronger new opportunities. Turn literature leads into falsifiable tests; prioritize real experiments over adding findings.

Resume with `python3 scripts/research_check.py` and `python3 scripts/research_status.py`, then inspect the next task. `python3 scripts/research_supervisor.py --dry-run` does not invoke a model. Paid work requires explicit `--start` and configured finite limits. Never enable background services or bypass sandbox, quota, rate limits, or user authorization. Supervisor checkpoints and records failures; inspect `git status` before/after and preserve existing edits. Update machine/human state after meaningful work. Do not claim execution beyond this session without an actually running supervisor.

Before every experiment, freeze the hypothesis, competing explanations, data/version, command, seed/configuration, metrics, uncertainty, exclusions, budget, and falsification gate. Verify raw artifacts and rerun relevant tests. Use independent units for uncertainty and record exact results including nulls. Report what ran and what remains unverified precisely. Stop on actual blockers, budget, session end, user stop, or completed objectives—not merely a rejected lead.
