# The Case of the Silent Sliders — Spotify Retention Investigation

A 9-page Streamlit app investigating Spotify retention using `pandas` +
`plotly.express` only — no SQL, no HTML/CSS injection, no interview-prep
filler. Built with `st.navigation` / `st.Page` (Streamlit ≥ 1.36).

## Setup

```bash
pip install -r requirements.txt
```

Place your three source files in `data/`:

```
data/
  users.csv                # user_id, city, city_tier, signup_date,
                            # account_age_days, subscription_type, retained_30_days
  listening_activity.csv   # user_id, avg_daily_listening_hours, skip_rate_pct
  engagement_metrics.csv   # user_id, playlist_adds_last_30d, search_queries_last_30d
```

## Run

```bash
streamlit run app.py
```

## Structure

```
app.py                          # entry point, st.navigation routing
.streamlit/config.toml          # Spotify-style dark theme
utils/
  data_loader.py                # @st.cache_data load/clean/merge + logistic regression
  styling.py                    # shared plotly dark-theme helper (not strictly requested,
                                 # but keeps every chart consistent without repeating code)
views/
  executive_summary.py          # 1. Executive Summary
  investigation_design.py       # 2. Investigation Design
  process_of_elimination.py     # 3. Process of Elimination
  statistical_validation.py     # 4. Statistical Validation
  hidden_signal.py               # 5. The Hidden Signal
  root_cause_diagnosis.py       # 6. Root Cause Diagnosis
  segment_cuts.py                # 7. Segment Cuts
  human_cost.py                   # 8. The Human Cost
  recommendation.py               # 9. Recommendation
```

## Notes on the cleaning logic (`utils/data_loader.py`)

- `account_age_days` is **recomputed** from `signup_date` (using the most
  recent signup in the file as the implicit snapshot date), since the raw
  column can disagree with `signup_date` or be missing.
- `skip_rate_pct` is clipped to `[0, 100]`; `avg_daily_listening_hours` is
  clipped to a max of `24` — both columns can contain physically impossible
  values in messy exports.
- Missing values in the four behavioral columns are imputed with the column
  median. Before doing this on your own data, check whether missingness
  correlates with the target — if it doesn't (it didn't here), imputing is
  safe and preserves your full sample.
- Nothing in the app hardcodes a result number (e.g. "93%", "98×"). Every
  statistic is computed live from whatever is in `data/` when you run it —
  the numbers in the on-page narrative copy describe the *shape* of the
  finding, not a literal value baked into the code.
