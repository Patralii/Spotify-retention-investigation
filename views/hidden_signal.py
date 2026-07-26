"""views/hidden_signal.py — Page 5: The Hidden Signal"""

import plotly.express as px
import streamlit as st

from utils.data_loader import load_data
from utils.styling import COLORS, style_fig

st.title("🎯 The Hidden Signal")
st.caption('The "Engagement Paradox" — more listening is not more loyalty')

df = load_data()

retained = df[df["churned"] == 0]
churned = df[df["churned"] == 1]

st.markdown(
    "The naive assumption is that heavier listeners are more engaged and less "
    "likely to churn. Side by side, the data says otherwise:"
)

m1, m2, m3, m4 = st.columns(4)

listen_gap = churned["avg_daily_listening_hours"].mean() - retained["avg_daily_listening_hours"].mean()
skip_gap = churned["skip_rate_pct"].mean() - retained["skip_rate_pct"].mean()
playlist_gap = churned["playlist_adds_last_30d"].mean() - retained["playlist_adds_last_30d"].mean()
search_gap = churned["search_queries_last_30d"].mean() - retained["search_queries_last_30d"].mean()

m1.metric(
    "Listening Hours/Day (churned)",
    f"{churned['avg_daily_listening_hours'].mean():.2f}",
    f"{listen_gap:+.2f} vs. retained",
    delta_color="inverse",
)
m2.metric(
    "Skip Rate (churned)",
    f"{churned['skip_rate_pct'].mean():.1f}%",
    f"{skip_gap:+.1f} pts vs. retained",
    delta_color="inverse",
)
m3.metric(
    "Playlist Adds, 30d (churned)",
    f"{churned['playlist_adds_last_30d'].mean():.2f}",
    f"{playlist_gap:+.2f} vs. retained",
    delta_color="inverse" if playlist_gap > 0 else "normal",
)
m4.metric(
    "Search Queries, 30d (churned)",
    f"{churned['search_queries_last_30d'].mean():.1f}",
    f"{search_gap:+.1f} vs. retained",
    delta_color="inverse" if search_gap > 0 else "normal",
)

st.divider()

c1, c2 = st.columns(2)

with c1:
    skip_compare = (
        df.groupby(df["churned"].map({0: "Retained", 1: "Churned"}))["skip_rate_pct"]
        .mean()
        .reset_index()
        .rename(columns={"churned": "Status"})
    )
    fig = px.bar(
        skip_compare,
        x="Status",
        y="skip_rate_pct",
        color="Status",
        color_discrete_map={"Retained": COLORS["green"], "Churned": COLORS["red"]},
        labels={"skip_rate_pct": "Avg. Skip Rate (%)"},
        title="Skip Rate: Retained vs. Churned",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(style_fig(fig, height=340), use_container_width=True)

with c2:
    playlist_compare = (
        df.groupby(df["churned"].map({0: "Retained", 1: "Churned"}))["playlist_adds_last_30d"]
        .mean()
        .reset_index()
        .rename(columns={"churned": "Status"})
    )
    fig2 = px.bar(
        playlist_compare,
        x="Status",
        y="playlist_adds_last_30d",
        color="Status",
        color_discrete_map={"Retained": COLORS["green"], "Churned": COLORS["red"]},
        labels={"playlist_adds_last_30d": "Avg. Playlist Adds (30d)"},
        title="Playlist Curation: Retained vs. Churned",
    )
    fig2.update_layout(showlegend=False)
    st.plotly_chart(style_fig(fig2, height=340), use_container_width=True)

st.warning(
    "**Why this would be easy to miss:** a dashboard that only tracks total "
    "listening hours as a health metric would flag churning users as the "
    "platform's *most* engaged listeners — right up until they leave. The "
    "features that actually separate retained from churned users are about "
    "*how* people listen (skipping) and what else they do around listening "
    "(curating, searching), not how much."
)
