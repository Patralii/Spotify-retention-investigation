"""views/executive_summary.py — Page 1: Executive Summary"""

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data_loader import get_kpis, load_data
from utils.styling import COLORS, style_fig

st.title("🔍 The Case of the Silent Sliders")
st.caption("Spotify Retention Investigation — Executive Summary")

df = load_data()
kpis = get_kpis(df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Users", f"{kpis['n_users']:,}")
col2.metric("30-Day Retention", f"{kpis['overall_retention'] * 100:.1f}%")
col3.metric(
    "Overall Churn",
    f"{kpis['overall_churn'] * 100:.1f}%",
)
col4.metric(
    "Disengaged Segment Odds Ratio",
    f"{kpis['odds_ratio']:.1f}×" if pd.notna(kpis["odds_ratio"]) else "—",
    help=(
        "Odds of churning for users with zero playlist adds and 5 or fewer "
        "search queries in the last 30 days, vs. everyone else."
    ),
)

st.divider()

with st.container(border=True):
    st.subheader("📌 Recommendation")
    if pd.notna(kpis["disengaged_churn"]) and pd.notna(kpis["other_churn"]):
        st.info(
            f"**Build a Lapsed Curation Alert.** Churn is not evenly spread across the "
            f"user base — it concentrates in users who've stopped curating. "
            f"**{kpis['disengaged_pct'] * 100:.1f}%** of users ({kpis['disengaged_n']:,}) "
            f"show zero playlist adds and minimal search activity in the last 30 days, "
            f"and that group churns at **{kpis['disengaged_churn'] * 100:.1f}%**, vs. "
            f"**{kpis['other_churn'] * 100:.1f}%** for everyone else. "
            f"See **Segment Cuts** for who this segment actually is, and **Recommendation** "
            f"for the proposed feature and rollout plan."
        )
    else:
        st.warning("Not enough data to compute the disengaged-segment comparison.")

st.subheader("Where churn concentrates")
c1, c2 = st.columns(2)

with c1:
    sub_churn = (
        df.groupby("subscription_type")["churned"].mean().reset_index()
    )
    sub_churn["churned"] *= 100
    fig = px.bar(
        sub_churn,
        x="subscription_type",
        y="churned",
        color="subscription_type",
        color_discrete_sequence=[COLORS["green"], COLORS["red"], COLORS["amber"]],
        labels={"churned": "Churn Rate (%)", "subscription_type": "Plan"},
        title="Churn Rate by Subscription Type",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(style_fig(fig), use_container_width=True)

with c2:
    age_churn = (
        df.groupby("age_bucket", observed=True)["churned"].mean().reset_index()
    )
    age_churn["churned"] *= 100
    fig2 = px.bar(
        age_churn,
        x="age_bucket",
        y="churned",
        labels={"churned": "Churn Rate (%)", "age_bucket": "Account Age"},
        title="Churn Rate by Account Tenure",
    )
    fig2.update_traces(marker_color=COLORS["green"])
    st.plotly_chart(style_fig(fig2), use_container_width=True)

st.caption(
    "City and city tier are checked and ruled out on the **Process of Elimination** page — "
    "the real story runs through plan type, tenure, and curation behavior."
)
