"""Optional lightweight dashboard; run with `streamlit run dashboard.py` when installed."""

import json
from pathlib import Path

REPORT = Path("results/paper5_pilot.json")

try:
    import streamlit as st
except ImportError:  # pragma: no cover - optional UI dependency
    raise SystemExit("Install the optional dashboard dependency to run this UI: streamlit")

st.title("Paper 5 research pilot")
if not REPORT.exists():
    st.info("Run PYTHONPATH=src python3 scripts/run_pilot.py first.")
else:
    report = json.loads(REPORT.read_text())
    st.metric("Resolved rate", f"{report['resolved_rate']:.1%}")
    st.json(report)

