"""views/process_of_elimination.py — Page 3: Process of Elimination"""

import plotly.express as px
import streamlit as st
from scipy import stats

from utils.data_loader import load_data
from utils.styling import COLORS, style_fig

st.title("🔍 Process of Elimination")
st.caption("Acting like a PM investigating a churn spike: rule out the easy answers first")

df = load_data()

st.subheader("Suspect #1: Geography")
c1, c2 = st.columns(2)

with c1:
    tier_churn = df.groupby("city_tier")["churned"].mean().reset_index()
    tier_churn["churned"] *= 100
    fig = px.bar(
        tier_churn,
        x="city_tier",
        y="churned",
        labels={"churned": "Churn Rate (%)", "city_tier": "City Tier"},
        title="Churn Rate by City Tier",
    )
    fig.update_traces(marker_color=COLORS["gray"])
    st.plotly_chart(style_fig(fig, height=320), use_container_width=True)

with c2:
    ct = (
        df.groupby("city_tier")["churned"]
        .agg(["sum", "count"])
        .rename(columns={"sum": "churned", "count": "total"})
    )
    ct["retained"] = ct["total"] - ct["churned"]
    chi2, p, dof, _ = stats.chi2_contingency(ct[["churned", "retained"]])
    st.metric("Chi-Square Statistic", f"{chi2:.2f}")
    st.metric("p-value", f"{p:.3f}")
    if p > 0.05:
        st.success(
            f"**Ruled out.** No statistically significant association between city "
            f"tier and churn (p = {p:.3f}). Tier 1 and Tier 2 churn within a fraction "
            f"of a point of each other."
        )
    else:
        st.warning(f"City tier shows a significant association with churn (p = {p:.3f}).")

st.divider()

st.subheader("Suspect #2: Subscription Type — the Premium Red Herring")

sub_churn = df.groupby("subscription_type")["churned"].mean().reset_index()
sub_churn["churned"] *= 100
fig2 = px.bar(
    sub_churn,
    x="subscription_type",
    y="churned",
    color="subscription_type",
    color_discrete_sequence=[COLORS["green"], COLORS["red"], COLORS["amber"]],
    labels={"churned": "Churn Rate (%)", "subscription_type": "Plan"},
    title="Churn Rate by Subscription Type — looks like an answer...",
)
fig2.update_layout(showlegend=False)
st.plotly_chart(style_fig(fig2, height=320), use_container_width=True)

st.markdown("**...but does it hold up once you control for tenure?**")

seg_churn = (
    df.groupby(["subscription_type", "tenure_group"])["churned"]
    .mean()
    .reset_index()
)
seg_churn["churned"] *= 100
fig3 = px.bar(
    seg_churn,
    x="subscription_type",
    y="churned",
    color="tenure_group",
    barmode="group",
    color_discrete_sequence=[COLORS["blue"], COLORS["red"]],
    labels={"churned": "Churn Rate (%)", "subscription_type": "Plan", "tenure_group": "Tenure"},
    title="Churn Rate by Subscription Type, Split by Tenure",
)
st.plotly_chart(style_fig(fig3, height=360), use_container_width=True)

new_premium = df[(df["subscription_type"] == "Premium") & (df["tenure_group"] == "New (<1yr)")]["churned"].mean() * 100
est_premium = df[(df["subscription_type"] == "Premium") & (df["tenure_group"] == "Established (1yr+)")]["churned"].mean() * 100

st.error(
    f"**Subscription type, eliminated as the *sole* root cause.** New Premium "
    f"subscribers churn at **{new_premium:.1f}%** — not far from Free/Family. "
    f"Established Premium subscribers churn at **{est_premium:.1f}%**. "
    f"'Premium' alone doesn't explain the gap; it only shows up once tenure is "
    f"factored in. Plan type is a *correlate* of the real risk pocket, not the cause "
    f"of it — confirmed statistically on the **Statistical Validation** page and "
    f"mapped out in full on **Segment Cuts**."
)
