"""views/investigation_design.py — Page 2: Investigation Design"""

import streamlit as st

from utils.data_loader import load_data

st.title("🧭 Investigation Design")
st.caption("North star, metric tree, and what this dataset can and can't tell us")

df = load_data()

st.subheader("North Star")
with st.container(border=True):
    st.markdown("### 🎯 30-Day Retention — `retained_30_days`")
    st.write(
        "A binary flag: did the user remain active 30 days after the snapshot? "
        "It's provided directly in the dataset rather than derived from a "
        "multi-week activity trail, which shapes the whole investigation — "
        "see the note at the bottom of this page."
    )

st.subheader("Metric Tree")
b1, b2, b3 = st.columns(3)

with b1:
    with st.container(border=True):
        st.markdown("**🧑‍🤝‍🧑 Demographic**")
        st.markdown(
            "- `city`\n"
            "- `city_tier`\n"
            "- `subscription_type`\n"
            "- `account_age_days`"
        )

with b2:
    with st.container(border=True):
        st.markdown("**🎧 Listening Behavior**")
        st.markdown(
            "- `avg_daily_listening_hours`\n"
            "- `skip_rate_pct`"
        )

with b3:
    with st.container(border=True):
        st.markdown("**📌 Curation Behavior**")
        st.markdown(
            "- `playlist_adds_last_30d`\n"
            "- `search_queries_last_30d`"
        )

st.divider()

st.subheader("Investigation Parameters")
params = {
    "Parameter": [
        "Dataset",
        "Structure",
        "Target",
        "Baseline churn",
        "Predictors available",
    ],
    "Value": [
        f"{len(df):,} users, 3 source tables",
        "Cross-sectional snapshot",
        "retained_30_days (binary)",
        f"{df['churned'].mean() * 100:.1f}%",
        "8 (4 demographic, 2 listening, 2 curation)",
    ],
}
st.dataframe(params, use_container_width=True, hide_index=True)

st.warning(
    "**What this dataset can't tell us:** there's no session-level time series here — "
    "no way to watch one user's engagement curve bend over weeks. Every behavioral "
    "feature (`playlist_adds_last_30d`, `skip_rate_pct`, etc.) and the "
    "`retained_30_days` label itself describe the *same trailing 30-day window*. "
    "That means a pattern like 'zero playlist adds predicts churn' could be a real "
    "leading indicator, or it could simply be two ways of describing the same "
    "disengagement at the same time. This gets called out again on the "
    "**Recommendation** page, where it actually matters for what to build."
)
