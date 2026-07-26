"""
app.py — entry point for "The Case of the Silent Sliders".

Run with:  streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="The Case of the Silent Sliders",
    page_icon="🎧",
    layout="wide",
)

pages = [
    st.Page("views/executive_summary.py", title="Executive Summary", icon="📊", default=True),
    st.Page("views/investigation_design.py", title="Investigation Design", icon="🧭"),
    st.Page("views/process_of_elimination.py", title="Process of Elimination", icon="🔍"),
    st.Page("views/statistical_validation.py", title="Statistical Validation", icon="📈"),
    st.Page("views/hidden_signal.py", title="The Hidden Signal", icon="🎯"),
    st.Page("views/root_cause_diagnosis.py", title="Root Cause Diagnosis", icon="🩺"),
    st.Page("views/segment_cuts.py", title="Segment Cuts", icon="🧩"),
    st.Page("views/human_cost.py", title="The Human Cost", icon="🧍"),
    st.Page("views/recommendation.py", title="Recommendation", icon="✅"),
]

# position="hidden" stops Streamlit from auto-rendering the nav list at the
# top of the sidebar, so we can control ordering ourselves below.
pg = st.navigation(pages, position="hidden")

with st.sidebar:
    st.title("🎧 Silent Sliders")
    st.caption("Spotify Retention Investigation")
    st.divider()

    # Manual nav list, in order/position we want.
    for page in pages:
        st.page_link(page, icon=page.icon)

pg.run()
