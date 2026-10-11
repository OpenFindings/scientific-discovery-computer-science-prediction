# Research architecture

This repository implements a minimal, auditable core for Paper 5. The data path is:

`ResearchQuestion -> EvidenceGraph/Action planner -> SafeExecutor -> deterministic interpreter -> Bayesian updater -> ResearchMemory`

The executor is deliberately allow-listed and invokes subprocesses without a shell. The pilot benchmark uses transparent, deterministic cases so the workflow can be tested without pretending that a public benchmark has been downloaded or that an LLM has produced evidence.

Facts, hypotheses, observations, and interpretations have separate types. Evidence carries source version, timestamp, uncertainty, and an independence group. Raw execution output is retained as the observation; an interpretation cannot replace it.

## Variants

`planner` is the cost-aware information-gain baseline implemented here. `direct` is represented in the pilot runner as fixed action order. The full four-way LLM-controlled comparison remains pending model/provider and benchmark decisions; no unsupported result is reported.

