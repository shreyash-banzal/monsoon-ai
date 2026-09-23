"""
Environment and Checkpoint Verifier for MONSOON-AI
Verifies that all 3 required actual trained .joblib models and NetCDF dataset are present before running Streamlit.
"""

import sys
from pathlib import Path
import joblib

def verify():
    root = Path(__file__).resolve().parent
    models_dir = root / "models"
    data_dir = root / "data"

    print("==================================================")
    print("MONSOON-AI (SIH26080) Localhost Environment Check")
    print("==================================================")
    print(f"Project root: {root}")
    print(f"Python version: {sys.version.split()[0]}")
    print("--------------------------------------------------")

    required_models = [
        "regime_classifier.joblib",
        "bias_correctors.joblib",
        "heavy_rain_prob_model.joblib"
    ]

    all_models_found = True
    for model_file in required_models:
        path = models_dir / model_file
        if path.is_file():
            size_kb = path.stat().st_size / 1024
            print(f"  [FOUND] models/{model_file} ({size_kb:.1f} KB)")
            try:
                obj = joblib.load(path)
                print(f"          ↳ Successfully loaded: {type(obj).__name__}")
            except Exception as e:
                print(f"          ↳ [ERROR] Failed to unpickle: {e}")
                all_models_found = False
        else:
            print(f"  [MISSING] models/{model_file}")
            all_models_found = False

    print("--------------------------------------------------")
    nc_path = data_dir / "imd_monsoon_2022_2025.nc"
    if nc_path.is_file():
        size_mb = nc_path.stat().st_size / (1024 * 1024)
        print(f"  [FOUND] data/imd_monsoon_2022_2025.nc ({size_mb:.2f} MB)")
    else:
        print(f"  [INFO] data/imd_monsoon_2022_2025.nc is not found (Can be uploaded via UI)")

    print("==================================================")
    if all_models_found:
        print("✅ ALL 3 ACTUAL TRAINED MODELS VERIFIED.")
        print("Ready to launch: streamlit run app.py")
    else:
        print("🚨 ACTION REQUIRED: One or more actual trained .joblib models are missing.")
        print("Place your model files in the 'models/' directory with exact names:")
        for m in required_models:
            print(f"  - models/{m}")
    print("==================================================")

    return all_models_found

if __name__ == "__main__":
    verify()
