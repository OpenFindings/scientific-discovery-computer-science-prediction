# Reproducibility

Requires Python 3.12+. From the repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest
PYTHONPATH=src python3 scripts/run_pilot.py
PYTHONPATH=src python3 scripts/run_execution_study.py
```

The infrastructure pilot and executable comparison do not require network access, model credentials, or external datasets. The execution report contains every raw probe output and posterior. On macOS, the executor uses `sandbox-exec`; this managed Codex host blocks nested use, so the recorded run opts into the inherited managed sandbox fallback. A standalone runner without a supported sandbox fails closed.
