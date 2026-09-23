# MONSOON-AI Models Directory

Place the following three pre-trained machine learning model files in this directory:

1. `regime_classifier.joblib`:
   - Trained classifier (RandomForest, XGBoost, or LightGBM)
   - Predicts synoptic regime:
     - 0: Normal / Transition
     - 1: Active Monsoon
     - 2: Break Monsoon
     - 3: Monsoon Depression / LPS
     - 4: Offshore Trough / Convective Surge
   - Input Features: `[raw_nwp, u850, rh700, mslp_grad]`

2. `bias_correctors.joblib`:
   - Dictionary of regime-specific regressors (e.g. `{0: model_0, 1: model_1, 2: model_2, 3: model_3, 4: model_4}`) or a regime-conditioned pipeline.
   - Accurately adjusts rainfall forecasts based on regime-dependent bias signatures.

3. `heavy_rain_prob_model.joblib`:
   - Probabilistic classifier trained to predict the likelihood of extreme rainfall exceeding the IMD heavy rain threshold (≥ 64.5 mm/day).

*Note: If these files are not present when you launch `streamlit run app.py`, the application will display an onboarding warning and offer a 1-click button to automatically synthesize and save benchmark models directly into this folder.*
