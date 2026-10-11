# Reproducibility

Requires Python 3.12+. From the repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest
PYTHONPATH=src python3 scripts/run_pilot.py
PYTHONPATH=src python3 scripts/run_execution_study.py
```

The infrastructure pilot and executable comparison do not require network access, model credentials, or external datasets. The execution report contains every raw probe output and posterior. On macOS, the executor uses `sandbox-exec` with restricted reads, scratch-only writes, and network denial. This managed Codex host blocks nested use, so the recorded run uses `--managed-outer-sandbox` to rely on the already enforced parent sandbox. Use that flag only inside a managed sandbox; standalone runs fail closed if OS sandboxing is unavailable.
