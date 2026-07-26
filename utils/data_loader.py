"""
utils/data_loader.py

Centralized, cached data loading and feature engineering for the
"Case of the Silent Sliders" retention investigation app.

Expects three CSVs in ./data/, joined on user_id:
  - users.csv:               user_id, city, city_tier, signup_date,
                              account_age_days, subscription_type, retained_30_days
  - listening_activity.csv:  user_id, avg_daily_listening_hours, skip_rate_pct
  - engagement_metrics.csv:  user_id, playlist_adds_last_30d, search_queries_last_30d

No SQL, no hardcoded result numbers — every statistic in the app is computed
live from whatever is actually in ./data/ when the app runs.
"""

import numpy as np
import pandas as pd
import streamlit as st

DATA_DIR = "data"

AGE_BINS = [0, 30, 90, 180, 365, 730, 1095, np.inf]
AGE_LABELS = ["<30d", "30-90d", "90-180d", "180-365d", "1-2yr", "2-3yr", "3yr+"]


@st.cache_data(show_spinner="Loading and cleaning retention data...")
def load_data() -> pd.DataFrame:
    """Load the 3 source CSVs, join them, and apply a defensible cleaning pass."""

    users = pd.read_csv(f"{DATA_DIR}/users.csv")
    listening = pd.read_csv(f"{DATA_DIR}/listening_activity.csv")
    engagement = pd.read_csv(f"{DATA_DIR}/engagement_metrics.csv")

    df = users.merge(listening, on="user_id", how="left").merge(
        engagement, on="user_id", how="left"
    )

    # --- Recompute account_age_days from signup_date -----------------------
    # The raw account_age_days column can disagree with signup_date (and be
    # missing outright). signup_date is the more reliable source, so we
    # rebuild tenure from it using the most recent signup in the file as the
    # implicit "snapshot" date. This keeps the script portable — it doesn't
    # depend on today's system clock matching whenever the data was pulled.
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")
    snapshot_date = df["signup_date"].max()
    df["account_age_days"] = (snapshot_date - df["signup_date"]).dt.days

    # --- Clip physically impossible values ----------------------------------
    df["skip_rate_pct"] = df["skip_rate_pct"].clip(lower=0, upper=100)
    df["avg_daily_listening_hours"] = df["avg_daily_listening_hours"].clip(upper=24)

    # --- Impute missing behavioral metrics with the column median ----------
    # (Check first that missingness isn't informative before doing this in
    # your own analysis — see the Statistical Validation page for the
    # underlying logic. For this dataset it was safe.)
    impute_cols = [
        "playlist_adds_last_30d",
        "search_queries_last_30d",
        "skip_rate_pct",
        "avg_daily_listening_hours",
        "account_age_days",
    ]
    for col in impute_cols:
        df[col] = df[col].fillna(df[col].median())

    # --- Feature engineering shared across every page ----------------------
    df["churned"] = 1 - df["retained_30_days"]

    df["age_bucket"] = pd.cut(df["account_age_days"], bins=AGE_BINS, labels=AGE_LABELS)

    df["tenure_group"] = np.where(
        df["account_age_days"] < 365, "New (<1yr)", "Established (1yr+)"
    )
    df["plan_group"] = np.where(
        df["subscription_type"] == "Premium", "Premium", "Free/Family"
    )
    df["segment"] = df["tenure_group"] + ", " + df["plan_group"]

    # The "Silent Slider": zero curation, almost no search activity.
    df["disengaged"] = (df["playlist_adds_last_30d"] == 0) & (
        df["search_queries_last_30d"] <= 5
    )

    df["skip_decile"] = (
        pd.qcut(df["skip_rate_pct"], 10, labels=False, duplicates="drop") + 1
    )
    df["listening_decile"] = (
        pd.qcut(df["avg_daily_listening_hours"], 10, labels=False, duplicates="drop") + 1
    )

    return df


@st.cache_data(show_spinner="Fitting the logistic regression...")
def fit_churn_model(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardized logistic regression predicting retained_30_days from every
    available demographic + behavioral feature at once. Returns a tidy
    coefficient table sorted from strongest risk factor to strongest
    protective factor.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    model_df = df.copy()
    model_df["is_premium"] = (model_df["subscription_type"] == "Premium").astype(int)
    model_df["is_family"] = (model_df["subscription_type"] == "Family").astype(int)
    model_df["is_tier1"] = (model_df["city_tier"] == "Tier 1").astype(int)

    feature_cols = [
        "account_age_days",
        "avg_daily_listening_hours",
        "skip_rate_pct",
        "playlist_adds_last_30d",
        "search_queries_last_30d",
        "is_premium",
        "is_family",
        "is_tier1",
    ]
    feature_labels = {
        "account_age_days": "Account Age",
        "avg_daily_listening_hours": "Listening Hours/Day",
        "skip_rate_pct": "Skip Rate",
        "playlist_adds_last_30d": "Playlist Adds (30d)",
        "search_queries_last_30d": "Search Queries (30d)",
        "is_premium": "Premium Plan",
        "is_family": "Family Plan",
        "is_tier1": "Tier 1 City",
    }

    X = model_df[feature_cols]
    y = model_df["retained_30_days"]

    X_scaled = StandardScaler().fit_transform(X)

    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_scaled, y)

    coef_df = pd.DataFrame(
        {
            "feature": [feature_labels[c] for c in feature_cols],
            "coefficient": clf.coef_[0],
        }
    )
    coef_df["odds_ratio"] = np.exp(coef_df["coefficient"])
    coef_df["direction"] = np.where(
        coef_df["coefficient"] < 0, "Risk factor", "Protective"
    )
    coef_df = coef_df.sort_values("coefficient").reset_index(drop=True)
    coef_df.attrs["accuracy"] = float(clf.score(X_scaled, y))
    return coef_df


@st.cache_data
def get_kpis(df: pd.DataFrame) -> dict:
    """Headline numbers used on the Executive Summary page."""
    overall_churn = df["churned"].mean()
    disengaged_mask = df["disengaged"]

    disengaged_churn = (
        df.loc[disengaged_mask, "churned"].mean() if disengaged_mask.any() else np.nan
    )
    other_churn = (
        df.loc[~disengaged_mask, "churned"].mean()
        if (~disengaged_mask).any()
        else np.nan
    )

    odds_ratio = np.nan
    if pd.notna(disengaged_churn) and pd.notna(other_churn):
        if 0 < disengaged_churn < 1 and 0 < other_churn < 1:
            odds_ratio = (disengaged_churn / (1 - disengaged_churn)) / (
                other_churn / (1 - other_churn)
            )

    return {
        "n_users": len(df),
        "overall_churn": overall_churn,
        "overall_retention": 1 - overall_churn,
        "disengaged_n": int(disengaged_mask.sum()),
        "disengaged_pct": disengaged_mask.mean(),
        "disengaged_churn": disengaged_churn,
        "other_churn": other_churn,
        "odds_ratio": odds_ratio,
    }


@st.cache_data
def get_profile_examples(df: pd.DataFrame) -> dict:
    """
    Dynamically select 3 representative real users for the Human Cost page.
    Nothing here is hardcoded to a specific user_id — it re-selects from
    whatever data is actually loaded, every run.
    """
    profiles = {}

    # A — long-tenured, disengaged, churned Premium subscriber.
    cand_a = df[df["disengaged"] & (df["churned"] == 1) & (df["subscription_type"] == "Premium")]
    if not cand_a.empty:
        profiles["long_tenure_churned_premium"] = (
            cand_a.sort_values("account_age_days", ascending=False).iloc[0]
        )

    # B — new, retained, above-median engagement Free/Family user.
    med_playlist = df["playlist_adds_last_30d"].median()
    cand_b = df[
        (df["churned"] == 0)
        & (df["plan_group"] == "Free/Family")
        & (df["account_age_days"] < 180)
        & (df["playlist_adds_last_30d"] >= med_playlist)
    ]
    if not cand_b.empty:
        profiles["new_retained_free"] = (
            cand_b.sort_values("account_age_days").iloc[0]
        )

    # C — mid-tenure churned user with high skip rate despite some curation
    #     (i.e. someone a zero-playlist-adds rule alone would have missed).
    skip_q75 = df["skip_rate_pct"].quantile(0.75)
    cand_c = df[
        (df["churned"] == 1)
        & df["account_age_days"].between(180, 500)
        & (df["skip_rate_pct"] > skip_q75)
        & (df["playlist_adds_last_30d"] >= 1)
    ]
    if not cand_c.empty:
        profiles["mid_tenure_high_skip"] = (
            cand_c.sort_values("avg_daily_listening_hours", ascending=False).iloc[0]
        )

    return profiles
