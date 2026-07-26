"""views/human_cost.py — Page 8: The Human Cost"""

import pandas as pd
import streamlit as st

from utils.data_loader import get_profile_examples, load_data

st.title("🧍 The Human Cost")
st.caption(
    "Three real, anonymized users from the dataset, identified only by user_id — "
    "selected dynamically from whichever data is actually loaded"
)

df = load_data()
profiles = get_profile_examples(df)

medians = {
    "account_age_days": df["account_age_days"].median(),
    "playlist_adds_last_30d": df["playlist_adds_last_30d"].median(),
    "search_queries_last_30d": df["search_queries_last_30d"].median(),
    "avg_daily_listening_hours": df["avg_daily_listening_hours"].median(),
    "skip_rate_pct": df["skip_rate_pct"].median(),
}


def render_profile(row: pd.Series, narrative: str, box):
    st.subheader(
        f"User #{int(row['user_id'])} — {row['city']} ({row['city_tier']}), "
        f"{row['subscription_type']}"
    )
    status = "Retained ✅" if row["churned"] == 0 else "Churned ❌"
    st.caption(f"{row['account_age_days']:.0f} days on the platform · {status}")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Account Age", f"{row['account_age_days']:.0f}d",
              f"{row['account_age_days'] - medians['account_age_days']:+.0f}d vs. median")
    m2.metric("Playlist Adds", f"{row['playlist_adds_last_30d']:.0f}",
              f"{row['playlist_adds_last_30d'] - medians['playlist_adds_last_30d']:+.1f} vs. median")
    m3.metric("Search Queries", f"{row['search_queries_last_30d']:.0f}",
              f"{row['search_queries_last_30d'] - medians['search_queries_last_30d']:+.1f} vs. median")
    m4.metric("Listening Hrs/Day", f"{row['avg_daily_listening_hours']:.2f}",
              f"{row['avg_daily_listening_hours'] - medians['avg_daily_listening_hours']:+.2f} vs. median")
    m5.metric("Skip Rate", f"{row['skip_rate_pct']:.1f}%",
              f"{row['skip_rate_pct'] - medians['skip_rate_pct']:+.1f} pts vs. median",
              delta_color="inverse")

    box(narrative)


tab_labels = [
    "10-yr Churned Premium",
    "New Retained Free",
    "Mid-Tenure Churned",
]
tabs = st.tabs(tab_labels)

with tabs[0]:
    if "long_tenure_churned_premium" in profiles:
        render_profile(
            profiles["long_tenure_churned_premium"],
            "**The textbook case.** Years on the platform, paying for Premium, "
            "zero playlists added and almost no searching in the last month — "
            "listening for hours a day but skipping most of it. This is exactly "
            "the profile a Lapsed Curation Alert is built to catch.",
            st.warning,
        )
    else:
        st.info("No user matched this profile in the currently loaded data.")

with tabs[1]:
    if "new_retained_free" in profiles:
        render_profile(
            profiles["new_retained_free"],
            "**What healthy engagement looks like.** New to the platform, on the "
            "free tier, and already curating and searching well above the "
            "median — modest listening volume but a low skip rate. By every "
            "measure that predicts retention here, this is a low-risk user, "
            "despite paying nothing.",
            st.success,
        )
    else:
        st.info("No user matched this profile in the currently loaded data.")

with tabs[2]:
    if "mid_tenure_high_skip" in profiles:
        render_profile(
            profiles["mid_tenure_high_skip"],
            "**Why playlist adds alone isn't enough.** This user kept adding "
            "playlists and still churned — a zero-adds rule would have missed "
            "them entirely. What gives them away is the skip rate. A real "
            "monitor needs the skip-rate cliff as a second tripwire, not just "
            "the playlist-adds cliff.",
            st.warning,
        )
    else:
        st.info("No user matched this profile in the currently loaded data.")
