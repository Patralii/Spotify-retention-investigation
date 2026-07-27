# The Case of the Silent Sliders
### Why Spotify's Most Loyal Listeners Aren't Who the Platform Thinks

## 🚀 Live App

**Streamlit App:** https://hqpcqrbk4jwvadkockm8fz.streamlit.app/

> **Project type:** Churn Driver Investigation + Behavioral Segment Analysis
> **Analyst:** Patrali Mondal
> **Dataset:** 100,000 users · 3 source tables · Single retention snapshot (Jun 2026)
> **Method:** Hypothesis-driven EDA · Chi-square testing · Logistic Regression · Decile Analysis

---

## The One-Sentence Finding

Listening volume is a **misleading retention metric** — churned users listen **75% more hours per day** than retained users, yet skip twice as often and make zero playlist adds, concentrating **26.8% platform churn** almost entirely in one segment: established Premium subscribers who stopped curating.

---

## The Narrative (9 Acts)

| Act | Page | What Happens |
|-----|------|-------------|
| I   | Executive Summary | Baseline churn is 26.8%. Three segments sit near 15%. One sits at 47.4%. The investigation begins. |
| II  | Investigation Design | North star locked: `retained_30_days`. Metric tree built across demographic, listening, and curation branches before a single chart is drawn. |
| III | Process of Elimination | Geography tested and eliminated (p = 0.61). Subscription type looks like an answer — until tenure is introduced as a second dimension. |
| IV  | Statistical Validation | Logistic regression controls for all 8 features simultaneously. Skip rate emerges as the single strongest churn predictor — stronger than plan, stronger than tenure. |
| V   | The Hidden Signal | The Engagement Paradox: churned users listen 4.03 hrs/day vs. 2.30 hrs for retained users. Volume is not loyalty. |
| VI  | Root Cause Diagnosis | The cliff edges: zero playlist adds = 75.4% churn vs. 12.5% for anyone who adds even one. Top-decile skip rate = 85.3% churn vs. 20.3% for everyone else. |
| VII | Segment Cuts | The 2×2 matrix reveals that established Premium subscribers (22.7% of users) hold 93% of all disengaged users and churn at 47.4% — 3× the platform average. |
| VIII| The Human Cost | Three real user profiles from the dataset — a 10-year churned Premium user, a 6-week retained Free user, a mid-tenure user the zero-adds rule would have missed. |
| IX  | Recommendation | A Lapsed Curation Alert: zero playlist adds as the primary trigger, top-decile skip rate as a secondary tripwire. Validated with a 50/50 A/B test before full rollout. |

---

## How to Run

### 1. Clone and install dependencies
```bash
git clone <your-repo-url>
cd silent_sliders_app
pip install -r requirements.txt
```

### 2. Data is already included
The `data/` folder contains all three source files — 100,000 rows each, pre-generated with realistic distributions and intentional data quality issues for the cleaning pipeline to handle.

```
data/
  users.csv                 # user_id, city, city_tier, signup_date,
                            # account_age_days, subscription_type, retained_30_days
  listening_activity.csv    # user_id, avg_daily_listening_hours, skip_rate_pct
  engagement_metrics.csv    # user_id, playlist_adds_last_30d, search_queries_last_30d
```

### 3. Launch the app
```bash
streamlit run app.py
```

Navigate to `localhost:8501`. The app loads, cleans, and caches all data on first run. Every subsequent page click is instant.

---

## The Four Risk Segments

| Segment | Users | Churn Rate | Avg Skip Rate | Avg Playlist Adds | Priority |
|---------|-------|-----------|---------------|-------------------|----------|
| New, Free/Family | 19,227 (19.2%) | 10.9% | 26.6% | 3.56 | Low |
| New, Premium | 13,007 (13.0%) | 11.7% | 26.8% | 3.53 | Watch |
| Established, Free/Family | 40,009 (40.0%) | 24.8% | 29.9% | 3.33 | Monitor |
| **Established, Premium** | **27,757 (27.8%)** | **47.7%** | **35.4%** | **2.83** | **Critical** |

Established Premium subscribers churn at **47.7%** — nearly 3× the platform average — despite listening the most hours per day. They hold **93% of all disengaged users** in the dataset.

---

## The Key Numbers

| Metric | Value |
|--------|-------|
| Total users | 100,000 |
| Overall churn rate | 26.8% |
| Overall retention rate | 73.2% |
| Established Premium churn | 47.7% |
| Disengaged segment size | 3,361 users (3.4%) |
| Disengaged segment churn | 78.5% |
| Everyone else churn | 25.0% |
| Zero playlist adds churn | 75.4% |
| One or more playlist adds churn | 12.5% |
| Top-decile skip rate churn | 85.3% |
| Bottom-9-decile skip rate churn | 20.3% |
| Churned avg listening hours/day | 4.03 hrs |
| Retained avg listening hours/day | 2.30 hrs |
| Churned avg skip rate | 47.3% |
| Retained avg skip rate | 24.0% |

---

## Key Technical Decisions

**Why recompute `account_age_days` from `signup_date` instead of imputing it?**
The raw column disagreed with `signup_date` on hundreds of rows — some by months, one implied a user had been on the platform for 37 years. Imputing a column that is already wrong in known ways builds on a broken foundation. `signup_date` is a timestamp written once at account creation and almost never corrupted. It is the more reliable source, so `account_age_days` was discarded and rebuilt entirely from it.

**Why clip invalid values instead of dropping the rows?**
A row with a skip rate of -45% or listening hours of 71 still contains a valid user_id, city, plan type, and retention label. Dropping it throws away everything correct in that row because one field is wrong. Clipping corrects only the broken measurement and preserves the rest.

**Why check whether missingness is informative before imputing?**
If users with missing skip rate data churn at a meaningfully different rate than users with complete data, the missing data has a pattern — imputing with the median would inject a false "average" into a group that is actually distinctive. In this dataset, retention rates for rows with missing values were within one percentage point of the full population across every behavioral column, confirming that missingness was random and median imputation was safe.

**Why use a left join when merging the three tables?**
`users.csv` is the source of truth — every user in the analysis must start from it. An inner join would silently drop users who exist in `users.csv` but have no matching row in `listening_activity.csv` or `engagement_metrics.csv`, potentially biasing the analysis if those users churn at a different rate. A left join keeps every user and surfaces missing behavioral data as NaN, which is then handled explicitly.

**Why run a logistic regression instead of stopping at groupby analysis?**
Groupby shows one variable at a time. The Premium/tenure confound — where plan type appeared to predict churn but was actually riding on tenure's correlation with both plan and churn — is invisible in a single-dimension groupby. Logistic regression controls for all eight features simultaneously and estimates each coefficient holding all others constant. That is the only way to confirm skip rate is independently predictive, not just correlated with other variables that drive churn.

**Why standardize features before the regression?**
Skip rate is measured in percentages (0–100). Account age is measured in days (0–3,650). Without standardization, a one-unit change in each has completely different meaning and the coefficients cannot be compared. Standardizing to mean 0 and standard deviation 1 puts every feature on the same scale so the coefficients are directly comparable — the largest absolute coefficient identifies the strongest independent predictor.

**Why propose an A/B test rather than immediately shipping the Lapsed Curation Alert?**
`playlist_adds_last_30d` and `retained_30_days` both describe the same trailing 30-day window. A user who decided to leave at the start of the month would naturally stop curating and not be retained in that same month — both are effects of the same underlying disengagement, not cause and effect. Observational data alone cannot determine whether zero playlist adds is a leading indicator (giving advance warning before the churn decision) or a lagging indicator (confirming a decision already made). Only a randomized experiment — 50% of flagged users receive the intervention, 50% do not — can resolve this.

---

## The Engagement Paradox

The most counterintuitive finding in the project, and the most important.

| Behavior | Retained Users | Churned Users |
|----------|---------------|---------------|
| Avg daily listening hours | 2.30 hrs | **4.03 hrs** |
| Avg skip rate | 24.0% | **47.3%** |
| Avg playlist adds (30d) | 3.98 | **1.29** |
| Avg search queries (30d) | 12.8 | 12.1 |

Churned users listen 75% more per day than retained users. A product dashboard tracking only total listening hours as a health metric would flag them as the platform's most engaged users — right up until they cancel.

The distinction is passive consumption vs intentional engagement. Churned users accept whatever the algorithm plays and skip most of it. Retained users search for artists they want, build playlists over time, and make the platform feel like theirs. Volume is not loyalty. Curation is.

---

## Data Quality Issues in the Raw Files

The dataset was generated with realistic data quality problems — the same categories that appear in real production exports.

| Issue | Count | Fix Applied |
|-------|-------|-------------|
| `account_age_days` missing | 4,519 rows | Recomputed from `signup_date` for all 100,000 rows |
| `account_age_days` inconsistent with `signup_date` | ~1,500 rows | Overwritten by recomputation |
| `skip_rate_pct` outside [0, 100] | 500 rows | Clipped to valid range |
| `avg_daily_listening_hours` above 24 | 1,001 rows | Clipped to 24 |
| `avg_daily_listening_hours` missing | 4,524 rows | Imputed with column median |
| `skip_rate_pct` missing | 4,915 rows | Imputed with column median |
| `playlist_adds_last_30d` missing | 3,077 rows | Imputed with column median |
| `search_queries_last_30d` missing | 3,004 rows | Imputed with column median |

All cleaning decisions are documented in `utils/data_loader.py` with inline comments explaining each choice. Nothing is cleaned silently.

---

**Total:** 1,111 lines of Python across 13 files.

---

## Skills Demonstrated

**Analytics:** Hypothesis-driven investigation · Churn driver analysis · Confound detection · Decile analysis · Behavioral segmentation · Cohort profiling

**Statistics:** Chi-square test of independence · Logistic regression · Feature standardization · Missingness analysis · Statistical vs practical significance

**Engineering:** Multi-table data joining · End-to-end cleaning pipeline · `@st.cache_data` for performance · Separated data / styling / page layers · Reproducible feature engineering

**Product thinking:** Metric tree design · Business translation of statistical findings · A/B test design · Leading vs lagging indicator distinction · Targeted vs platform-wide intervention framing

**Tools:** Python · Pandas · NumPy · SciPy · scikit-learn · Plotly · Streamlit · Google Colab

---

## Recruiter Signal

This project demonstrates **subscription product retention thinking** — not just user analytics. The framing is: a platform that optimizes for listening volume as a proxy for engagement is measuring the wrong thing. The users generating the most hours are also the ones most likely to leave — because volume without intentionality is not retention, it is passive consumption on the way out.

The Lapsed Curation Alert is a product feature, not just a dashboard finding. The A/B test design is a recognition that correlation in observational data is not a mandate to act — it is a hypothesis to test. The segment-specific targeting is a resource allocation argument: spend the retention budget where 93% of the problem actually lives, not spread it across the 77% of users who were never meaningfully at risk.

---

*Built by Patrali Mondal · Data Analyst · Product Analytics Portfolio · Google Data Analytics Apprenticeship Application*
