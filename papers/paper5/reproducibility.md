# Paper 5 reproducibility

The offline infrastructure requires Python 3.12+ and has no network or model
credential requirement for the controlled pilot.

```bash
PYTHONPATH=src python3 scripts/smoke_test.py
PYTHONPATH=src python3 scripts/run_pilot.py
PYTHONPATH=src python3 scripts/run_execution_study.py
PYTHONPATH=src python3 scripts/run_transfer.py
```

The transfer command reports the 26 source-linked candidates from
`data/research_questions.jsonl` while `data/questions.jsonl` is absent. It does
not score them. The candidate inventory is not yet the historical feature
registry: records need full-text review, pre-cutoff feature coding, and
independent future-label adjudication first.

The pilot output is `results/paper5_pilot.json`. A populated transfer run writes
`results/paper5_transfer.json`. Dashboard values distinguish verified pilot
observations from transfer forecasts and recommendations.

The execution/falsification comparison writes
`results/paper5_execution_falsification_pilot.json`. It runs deterministic
policies, not LLM agents, on four synthetic cases and makes no significance
claims. Its broad Wilson intervals and validity limitations are documented in
`pilot_results.md`.

The arXiv metadata harvest is a generated local dataset (`data/arxiv_cs_corpus.jsonl`,
about 1.6 GB) and is excluded from Git by `.gitignore`; its source query,
per-quarter result/retrieval ledger, date limits, and collection count are
tracked in `data/arxiv_cs_manifest.json`. Rebuild or resume it with
`python3 scripts/collect_arxiv_cs.py`; audit with
`python3 scripts/audit_arxiv_cs_corpus.py`. The API metadata and abstract
harvest is not a claim that these full texts have been downloaded, licensed for
redistribution, or manually analyzed.
