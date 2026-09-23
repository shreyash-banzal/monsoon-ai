# 🌧️ MONSOON-AI: Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts

[![Smart India Hackathon](https://img.shields.io/badge/SIH-SIH26080-blue.svg)](https://www.sih.gov.in/)
[![Python](https://img.shields.io/badge/Python-3.13-brightgreen.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

**MONSOON-AI** is an operational-grade prototype built for Smart India Hackathon problem statement **SIH26080**. It solves a fundamental limitation in conventional Numerical Weather Prediction (NWP) models (e.g., IMD GFS, NCMRWF NCUM, WRF): **systematic regime-dependent rainfall biases across the Indian Summer Monsoon season (June–September).**

---

## ⚠️ Model Requirements: Strict Trained Mode (No Synthetic Fallbacks)
In accordance with strict operational evaluation requirements:
- **No synthetic or heuristic fallbacks** are enabled for machine learning models.
- The pipeline strictly requires your **actual trained `.joblib` model files** in the `models/` directory.
- If any file is missing, the application halts pipeline inference and prompts for the exact files via the onboarding UI or directory placement.

---

## 📂 Project Structure
```
monsoon-ai/
├── app.py                      # Main Streamlit dashboard entry point
├── .env.example                # Sample API keys configuration
├── requirements.txt            # Python 3.13 dependencies
├── README.md                   # Full system documentation
├── verify_environment.py       # Pre-flight environment & checkpoint checker
├── models/                     # PLACE YOUR 3 TRAINED .JOBLIB FILES HERE
│   ├── regime_classifier.joblib      # Synoptic regime classifier
│   ├── bias_correctors.joblib        # Dict of regime-specific regressors
│   └── heavy_rain_prob_model.joblib  # Probabilistic extreme rain classifier
├── data/                       # PLACE YOUR NETCDF FILE HERE
│   └── imd_monsoon_2022_2025.nc      # IMD observation & NWP forecast grid
├── utils/
│   ├── inference.py            # Strict ML inference pipeline (no joblib fallbacks)
│   ├── metrics.py              # Verification metrics (RMSE, MAE, CSI, POD, FAR, ETS)
│   ├── llm_explainer.py        # Groq/Gemini LLM synoptic reasoning module
│   └── map_utils.py            # Folium & Plotly interactive meteorological maps
└── pages/
    ├── 1_Command_Center.py     # Real-time KPIs, active regime, hero forecast map
    ├── 2_Rainfall_Map.py       # Interactive layer switcher (Raw vs AI vs Difference vs Risk)
    ├── 3_Regime_AI.py          # Core USP: Pipeline inspection & LLM synoptic reasoning
    ├── 4_Heavy_Rain_Alerts.py  # IMD risk categorization (Yellow/Orange/Red) & district table
    ├── 5_Verification_Lab.py   # Rigorous statistical validation & regime-wise metrics
    └── 6_WhatIf_Simulator.py   # Interactive scenario simulator with LLM explanations
```

---

## 📍 Where to Add Your Files

### 1. Trained Machine Learning Checkpoints (`models/`)
Place your 3 trained files directly inside `monsoon-ai/models/`:
- **`models/regime_classifier.joblib`**:
  - Model predicting synoptic regime (0: Normal, 1: Active, 2: Break, 3: Depression/LPS, 4: Offshore Trough).
  - Expected input feature vector: `[raw_nwp, u850, rh700, mslp_grad]`
- **`models/bias_correctors.joblib`**:
  - Dictionary of regime-specific regressors (e.g. `{0: model_0, 1: model_1, 2: model_2, 3: model_3, 4: model_4}`) or an object implementing `.predict(X)`.
- **`models/heavy_rain_prob_model.joblib`**:
  - Calibrated classifier implementing `.predict_proba(X)` for probability of rainfall exceeding ≥ 64.5 mm/day.

### 2. NetCDF Observation & Forecast Grid (`data/`)
Place your processed NetCDF file inside `monsoon-ai/data/`:
- **`data/imd_monsoon_2022_2025.nc`**
- Coordinates: `time`, `lat`, `lon`
- Variables: `rainfall_obs`, `raw_nwp`, `u850`, `rh700`, `mslp`

---

## 💻 How to Setup and Run on Localhost

### Step 1: Clone / Export the Project
Extract or clone the project folder on your machine:
```bash
cd monsoon-ai
```

### Step 2: Create a Python 3.13 Virtual Environment
```bash
# On Linux / macOS:
python3 -m venv venv
source venv/bin/activate

# On Windows (Command Prompt):
python -m venv venv
venv\Scripts\activate.bat

# On Windows (PowerShell):
python -m venv venv
venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure API Key for LLM Explanations
Create your `.env` file from the template:
```bash
cp .env.example .env
```
Open `.env` in any text editor and insert your Groq or Gemini API key:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
# Optional: GEMINI_API_KEY=your_gemini_api_key_here
```

### Step 5: Place Your Trained Models
Copy your trained files into `models/`:
```bash
# Verify files exist in models/
ls -la models/
# Should show:
# regime_classifier.joblib
# bias_correctors.joblib
# heavy_rain_prob_model.joblib
```

You can run the built-in verifier script to test that all 3 models load cleanly:
```bash
python generate_sample_assets.py
```

### Step 6: Launch the Streamlit Application
```bash
streamlit run app.py
```
Streamlit will start local server and print:
```text
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```
Open `http://localhost:8501` in your browser!

---

## 📊 Verification Metrics Implemented
- **RMSE (Root Mean Square Error)**: Penalizes large spatial intensity errors.
- **MAE (Mean Absolute Error)**: Average magnitude of rainfall error (mm).
- **CSI (Critical Success Index / Threat Score)**: $CSI = \frac{Hits}{Hits + FalseAlarms + Misses}$
- **POD (Probability of Detection / Hit Rate)**: $POD = \frac{Hits}{Hits + Misses}$
- **FAR (False Alarm Ratio)**: $FAR = \frac{FalseAlarms}{Hits + FalseAlarms}$
- **ETS (Equitable Threat Score)**: Accounts for hits expected purely by chance.
