"""views/recommendation.py — Page 9: Recommendation"""

import pandas as pd
import streamlit as st

from utils.data_loader import get_kpis, load_data

st.title("✅ Recommendation")
st.caption("What to build, who to target, and the one caveat that determines whether it works")

df = load_data()
kpis = get_kpis(df)

with st.container(border=True):
    st.subheader("Proposed feature: Lapsed Curation Alert")
    st.info(
        "**Trigger:** flag any user whose `playlist_adds_last_30d` hits exactly 0, "
        "OR whose `skip_rate_pct` lands in the top decile of the platform.\n\n"
        "**Target:** established (1yr+) Premium subscribers specifically — see "
        "**Segment Cuts** for why this segment, not a platform-wide blast, is "
        "where the budget should go.\n\n"
        "**Response:** a personalized win-back nudge (e.g. a 'picks up where you "
        "left off' playlist), not a generic re-engagement push."
    )

st.subheader("Why this, specifically")
c1, c2, c3 = st.columns(3)
c1.metric("Disengaged users found", f"{kpis['disengaged_n']:,}", f"{kpis['disengaged_pct']*100:.1f}% of base")
c2.metric("Their churn rate", f"{kpis['disengaged_churn']*100:.1f}%" if pd.notna(kpis['disengaged_churn']) else "—")
c3.metric("Everyone else's churn rate", f"{kpis['other_churn']*100:.1f}%" if pd.notna(kpis['other_churn']) else "—")

st.divider()

st.subheader("Rollout plan")
with st.container(border=True):
    st.markdown(
        "1. **Instrument the alert** — `playlist_adds_last_30d == 0` is already in "
        "the existing engagement_metrics pipeline; no new tracking required to "
        "start flagging users.\n"
        "2. **Add the skip-rate tripwire** as a second signal for users the "
        "zero-adds rule misses (see the mid-tenure profile on **The Human Cost**).\n"
        "3. **Scope the win-back creative to established Premium subscribers** "
        "rather than a platform-wide campaign.\n"
        "4. **A/B test before full rollout** — 50% of flagged users get the "
        "intervention, 50% are held as control, minimum 30-day window."
    )

st.subheader("Risks to watch")
st.error(
    "**All 30-day features overlap with the target window.** "
    "`playlist_adds_last_30d` and `retained_30_days` may describe nearly the same "
    "period. A user who's already decided to leave will naturally stop curating "
    "and start skipping in that same window — which means this dashboard has "
    "*not yet proven* the alert gives advance warning rather than just confirming "
    "what's already happened. **The A/B test is how you find out:** if "
    "intervening on the flag changes outcomes, it's a leading indicator. If it "
    "doesn't, it was a lagging one."
)
st.warning(
    "**Notification fatigue.** Cap interventions at one per user per 30-day "
    "window and monitor the opt-out rate as a leading indicator of overreach."
)

st.success(
    "**What we are confident about:** the associations themselves aren't in "
    "doubt — the sample is large, the effects are large, and they hold up after "
    "controlling for every other variable in the regression on "
    "**Statistical Validation**. The open question is causal direction and lead "
    "time, not whether the pattern is real."
)
