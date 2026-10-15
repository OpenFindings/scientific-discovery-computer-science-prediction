"""Optional lightweight dashboard; run with `streamlit run dashboard.py` when installed."""

import json
from pathlib import Path

REPORT = Path("results/paper5_pilot.json")
TRANSFER = Path("results/paper5_transfer.json")
REGISTRY = Path("data/questions.jsonl")
CANDIDATES = Path("data/research_questions.jsonl")
EXECUTION = Path("results/paper5_execution_falsification_pilot.json")
CORPUS_PROFILE = Path("data/arxiv_cs_profile.json")

try:
    import streamlit as st
except ImportError:  # pragma: no cover - optional UI dependency
    raise SystemExit("Install the optional dashboard dependency to run this UI: streamlit")

st.title("Paper 5 research pilot")
st.caption("Verified observations, model forecasts, and recommendations are shown separately.")

st.subheader("Literature discovery corpus")
if CORPUS_PROFILE.exists():
    corpus = json.loads(CORPUS_PROFILE.read_text())
    st.metric("Unique arXiv CS records", f"{corpus['unique_records']:,}")
    st.caption(
        f"2010–2026 metadata/abstract harvest · {corpus['complete_quarter_cells']} complete quarter windows · "
        f"{corpus['abstract_coverage']:.0%} abstract coverage. Screening corpus only; full texts are not all reviewed."
    )
    left, right = st.columns(2)
    with left:
        st.write("Papers by year band")
        st.dataframe([{"period": period, "records": count}
                      for period, count in corpus["year_bands"].items()], hide_index=True)
    with right:
        st.write("Largest primary categories")
        st.dataframe([{"category": category, "records": count}
                      for category, count in list(corpus["top_20_primary_categories"].items())[:10]],
                     hide_index=True)
else:
    st.info("The literature discovery corpus profile has not been generated yet.")

if not REPORT.exists():
    st.info("Run PYTHONPATH=src python3 scripts/run_pilot.py first.")
else:
    report = json.loads(REPORT.read_text())
    st.metric("Resolved rate", f"{report['resolved_rate']:.1%}")
    st.subheader("Verified infrastructure pilot")
    st.json(report)

st.subheader("Paper 3 + Paper 4 transfer")
if not REGISTRY.exists():
    if CANDIDATES.exists():
        candidates = [json.loads(line) for line in CANDIDATES.read_text().splitlines() if line.strip()]
        st.info(f"{len(candidates)} source-cited candidate questions collected. Full-text coding and historical labels are not yet complete, so forecasts are not shown.")
        domains = sorted({item["domain"] for item in candidates})
        selected_domain = st.selectbox("Research area", ["All"] + domains)
        visible = candidates if selected_domain == "All" else [item for item in candidates if item["domain"] == selected_domain]
        for item in visible:
            with st.expander(f"{item['id']}: {item['question']}"):
                st.write(item["evidence_basis"])
                st.write("Suggested experiment:", item["experiment_suggestion"])
                for source in item["sources"]:
                    st.markdown(f"[Open paper]({source})")
    else:
        st.warning("No source-cited CS question registry is loaded.")
elif not TRANSFER.exists():
    st.info("A question registry is present; run scripts/run_transfer.py to generate the report.")
else:
    transfer = json.loads(TRANSFER.read_text())
    st.metric("Registered questions", transfer["n_questions"])
    st.json(transfer)

st.subheader("Execution and falsification pilot")
if EXECUTION.exists():
    execution = json.loads(EXECUTION.read_text())
    rows = []
    for name, summary in execution["summaries"].items():
        rows.append({"condition": name, "correct resolutions": summary["correct_resolutions"],
                     "correct provisional predictions": summary["correct_provisional_predictions"],
                     "unsupported conclusions": summary["unsupported_conclusions"],
                     "mean actions": summary["mean_actions"],
                     "counterevidence events": summary["counterevidence_events"]})
    st.dataframe(rows, hide_index=True)
    with st.expander("Question level execution traces"):
        st.json(execution["summaries"])
    st.caption(execution["caveat"])
else:
    st.info("Run scripts/run_execution_study.py to generate this pilot report.")
