# Reproducibility

Requires Python 3.12+. From the repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest
PYTHONPATH=src python3 scripts/run_pilot.py
```

The pilot is deterministic and writes a JSON report with raw observations and posterior beliefs. It does not require network access, model credentials, or external datasets.

