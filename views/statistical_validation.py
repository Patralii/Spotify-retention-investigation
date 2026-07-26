"""views/statistical_validation.py — Page 4: Statistical Validation"""

import plotly.express as px
import streamlit as st

from utils.data_loader import fit_churn_model, load_data
from utils.styling import COLORS, style_fig

st.title("📈 Statistical Validation")
st.caption(
    "A logistic regression controlling for every available feature at once — "
    "to rank what actually predicts churn, not just what correlates with it"
)

df = load_data()
coef_df = fit_churn_model(df)

top_risk = coef_df.iloc[0]
col1, col2, col3 = st.columns(3)
col1.metric("Top Risk Predictor", top_risk["feature"], f"β = {top_risk['coefficient']:.2f}")
col2.metric("Its Odds Ratio", f"{top_risk['odds_ratio']:.2f}×")
col3.metric("Model Accuracy", f"{coef_df.attrs.get('accuracy', 0) * 100:.1f}%")

st.divider()

st.subheader("Standardized coefficients")
st.caption(
    "Predicting `retained_30_days`. Negative = associated with churn risk, "
    "positive = protective. All features standardized so coefficients are "
    "directly comparable."
)

fig = px.bar(
    coef_df,
    x="coefficient",
    y="feature",
    orientation="h",
    color="direction",
    color_discrete_map={"Risk factor": COLORS["red"], "Protective": COLORS["green"]},
    labels={"coefficient": "Standardized Coefficient", "feature": ""},
)
fig.update_layout(showlegend=True)
st.plotly_chart(style_fig(fig, height=420), use_container_width=True)

st.subheader("Coefficient table")
display_df = coef_df.copy()
display_df["coefficient"] = display_df["coefficient"].round(3)
display_df["odds_ratio"] = display_df["odds_ratio"].round(3)
st.dataframe(
    display_df.rename(
        columns={
            "feature": "Feature",
            "coefficient": "Coefficient (std.)",
            "odds_ratio": "Odds Ratio",
            "direction": "Direction",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.success(
    f"**Why this matters more than the univariate cuts on Process of Elimination:** "
    f"plan type and tenure are correlated with each other, so a simple two-way table "
    f"can't tell you which one is doing the work. Controlling for both at once, "
    f"**{top_risk['feature']}** is still the single strongest predictor of churn in "
    f"this dataset — stronger than plan, stronger than tenure, stronger than raw "
    f"listening volume. That's the signal worth building a monitor around."
)
