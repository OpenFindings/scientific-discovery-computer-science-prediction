# Experiment registry

| ID | Status | Description | Output |
|---|---|---|---|
| P5-PILOT-001 | runnable | Deterministic four-case causal diagnosis pilot | `results/paper5_pilot.json` |
| P5-EXEC-FALSIFY-PILOT-001 | executed pilot | Four executable cases, including a hidden context confound, across five predeclared conditions | `results/paper5_execution_falsification_pilot.json` |
| P5-TRANSFER-001 | candidates collected; forecasting awaits coding | Paper 3 forecasts plus Paper 4 opportunity ranking on source-cited CS questions | `data/research_questions.jsonl`; enriched historical registry still required |
| P5-LIT-001 | candidate corpus collected | 26 source-linked candidate questions from 29 unique arXiv records | `data/research_questions.jsonl`; full-text coding pending |
| P5-FINAL | blocked | Matched direct, fixed workflow, Paper-4 transfer, and feedback agents | Requires verified Paper 4 implementation, benchmark/licence audit, and fixed model access |
| P6 | protocol only | Independent adversarial falsification | Not run; depends on validated Paper 5 executor |
| P7 | protocol only | Sequential adaptive replanning | Not run; depends on validated Paper 5 executor |
