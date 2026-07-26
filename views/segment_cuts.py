"""views/segment_cuts.py — Page 7: Segment Cuts"""

import plotly.express as px
import streamlit as st

from utils.data_loader import load_data
from utils.styling import COLORS, style_fig

st.title("🧩 Segment Cuts")
st.caption("Tenure × plan type — finding out which segment actually carries the risk")

df = load_data()
total_disengaged = int(df["disengaged"].sum())

matrix = (
    df.groupby(["tenure_group", "plan_group"])
    .agg(
        n_users=("user_id", "size"),
        churn_rate=("churned", "mean"),
        disengaged_n=("disengaged", "sum"),
    )
    .reset_index()
)
matrix["pct_of_users"] = matrix["n_users"] / len(df) * 100
matrix["churn_rate"] *= 100
matrix["pct_of_disengaged"] = (
    matrix["disengaged_n"] / total_disengaged * 100 if total_disengaged else 0
)
matrix["segment"] = matrix["tenure_group"] + ", " + matrix["plan_group"]

c1, c2 = st.columns(2)

with c1:
    fig = px.bar(
        matrix.sort_values("churn_rate"),
        x="churn_rate",
        y="segment",
        orientation="h",
        labels={"churn_rate": "Churn Rate (%)", "segment": ""},
        title="Churn Rate by Segment",
    )
    fig.update_traces(
        marker_color=[
            COLORS["red"] if v == matrix["churn_rate"].max() else COLORS["gray"]
            for v in matrix.sort_values("churn_rate")["churn_rate"]
        ]
    )
    st.plotly_chart(style_fig(fig, height=340), use_container_width=True)

with c2:
    fig2 = px.bar(
        matrix.sort_values("pct_of_disengaged"),
        x="pct_of_disengaged",
        y="segment",
        orientation="h",
        labels={"pct_of_disengaged": "% of All Disengaged Users", "segment": ""},
        title="Where the Disengaged Users Are",
    )
    fig2.update_traces(
        marker_color=[
            COLORS["red"] if v == matrix["pct_of_disengaged"].max() else COLORS["gray"]
            for v in matrix.sort_values("pct_of_disengaged")["pct_of_disengaged"]
        ]
    )
    st.plotly_chart(style_fig(fig2, height=340), use_container_width=True)

st.subheader("Four-segment summary table")
display_matrix = matrix[
    ["segment", "pct_of_users", "churn_rate", "pct_of_disengaged"]
].rename(
    columns={
        "segment": "Segment",
        "pct_of_users": "% of Users",
        "churn_rate": "Churn Rate (%)",
        "pct_of_disengaged": "% of Disengaged Users",
    }
)
st.dataframe(
    display_matrix.round(1),
    use_container_width=True,
    hide_index=True,
)

top_segment = matrix.loc[matrix["pct_of_disengaged"].idxmax()]
st.error(
    f"**One segment, most of the risk.** "
    f"**{top_segment['segment']}** subscribers are "
    f"**{top_segment['pct_of_users']:.1f}%** of all users but hold "
    f"**{top_segment['pct_of_disengaged']:.1f}%** of every disengaged user found, "
    f"churning at **{top_segment['churn_rate']:.1f}%** — far above any other "
    f"segment. This is not four equally important cuts; it's one segment that "
    f"needs an intervention and three that mostly don't."
)
