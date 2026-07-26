"""views/root_cause_diagnosis.py — Page 6: Root Cause Diagnosis"""

import plotly.express as px
import streamlit as st

from utils.data_loader import load_data
from utils.styling import COLORS, style_fig

st.title("🩺 Root Cause Diagnosis")
st.caption("Churn isn't a smooth slope here — it's a threshold")

df = load_data()

st.subheader("Cliff #1: Playlist adds")
st.caption("Churn rate by number of playlists added in the last 30 days")

playlist_churn = (
    df.groupby("playlist_adds_last_30d")["churned"]
    .agg(churn_rate="mean", n="size")
    .reset_index()
)
playlist_churn["churn_rate"] *= 100
# Keep bins with a reasonable sample size so the tail doesn't get noisy
playlist_churn = playlist_churn[playlist_churn["n"] >= 20].sort_values("playlist_adds_last_30d")

fig = px.bar(
    playlist_churn,
    x="playlist_adds_last_30d",
    y="churn_rate",
    labels={"playlist_adds_last_30d": "Playlist Adds (30d)", "churn_rate": "Churn Rate (%)"},
    title="Churn Rate by Playlist Adds — the cleanest cliff in the data",
)
fig.update_traces(
    marker_color=[
        COLORS["red"] if v == 0 else COLORS["gray"]
        for v in playlist_churn["playlist_adds_last_30d"]
    ]
)
st.plotly_chart(style_fig(fig), use_container_width=True)

zero_add_churn = df[df["playlist_adds_last_30d"] == 0]["churned"].mean() * 100
nonzero_add_churn = df[df["playlist_adds_last_30d"] > 0]["churned"].mean() * 100
st.error(
    f"Users with **zero** playlist adds churn at **{zero_add_churn:.1f}%**. "
    f"Anyone who adds even **one** playlist drops to **{nonzero_add_churn:.1f}%**. "
    f"This isn't a gradual decline — it's a switch."
)

st.divider()

st.subheader("Cliff #2: Skip rate")
st.caption("Churn rate by skip-rate decile (1 = lowest skip rate, 10 = highest)")

skip_decile_churn = (
    df.groupby("skip_decile")["churned"].mean().reset_index()
)
skip_decile_churn["churned"] *= 100
top_decile = skip_decile_churn["skip_decile"].max()

fig2 = px.bar(
    skip_decile_churn,
    x="skip_decile",
    y="churned",
    labels={"skip_decile": "Skip Rate Decile", "churned": "Churn Rate (%)"},
    title="Churn Rate by Skip Rate Decile",
)
fig2.update_traces(
    marker_color=[
        COLORS["red"] if d == top_decile else COLORS["gray"]
        for d in skip_decile_churn["skip_decile"]
    ]
)
fig2.update_xaxes(dtick=1)
st.plotly_chart(style_fig(fig2), use_container_width=True)

top_decile_churn = skip_decile_churn.loc[
    skip_decile_churn["skip_decile"] == top_decile, "churned"
].values[0]
rest_churn = skip_decile_churn.loc[
    skip_decile_churn["skip_decile"] != top_decile, "churned"
].mean()
st.error(
    f"Deciles 1–{int(top_decile) - 1} sit flat around **{rest_churn:.1f}%** churn. "
    f"The top skip-rate decile spikes to **{top_decile_churn:.1f}%**. Like playlist "
    f"adds, this is a threshold to alert on, not a trend to chart."
)

st.info(
    "Both cliffs feed directly into the **Recommendation** page's proposed "
    "Lapsed Curation Alert: zero playlist adds as the primary trigger, "
    "top-decile skip rate as a second tripwire for users the first rule misses."
)
