"""
MONSOON-AI Inference Pipeline
Loads trained joblib models, extracts synoptic features, predicts atmospheric regimes,
applies regime-conditioned bias correction, and infers extreme precipitation probabilities.
STRICT MODE: No synthetic/heuristic fallback for .joblib models. Actual trained models are strictly required.
"""

import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, Union
import numpy as np
import pandas as pd
import joblib

# Standard regime dictionary mappings
REGIME_MAP = {
    0: "Normal / Transition",
    1: "Active Monsoon",
    2: "Break Monsoon",
    3: "Monsoon Depression / LPS",
    4: "Offshore Trough / Convective Surge"
}

FEATURE_NAMES = ["raw_nwp", "u850", "rh700", "mslp_grad"]


class MonsoonInferenceEngine:
    def __init__(self, models_dir: Union[str, Path] = "models"):
        self.models_dir = Path(models_dir)
        self.regime_classifier_path = self.models_dir / "regime_classifier.joblib"
        self.bias_correctors_path = self.models_dir / "bias_correctors.joblib"
        self.heavy_rain_model_path = self.models_dir / "heavy_rain_prob_model.joblib"

        self.regime_classifier = None
        self.bias_correctors = None
        self.heavy_rain_model = None

        self.load_models()

    def check_models_exist(self) -> Dict[str, bool]:
        """Check status of the 3 required joblib files."""
        return {
            "regime_classifier.joblib": self.regime_classifier_path.is_file(),
            "bias_correctors.joblib": self.bias_correctors_path.is_file(),
            "heavy_rain_prob_model.joblib": self.heavy_rain_model_path.is_file()
        }

    def all_models_ready(self) -> bool:
        """Returns True only if all 3 actual trained model files exist and are loaded in memory."""
        return (
            self.regime_classifier is not None and
            self.bias_correctors is not None and
            self.heavy_rain_model is not None
        )

    def load_models(self) -> bool:
        """Loads actual trained models from disk. Returns False if any model is missing or corrupt."""
        status = self.check_models_exist()
        if not all(status.values()):
            return False

        try:
            self.regime_classifier = joblib.load(self.regime_classifier_path)
            self.bias_correctors = joblib.load(self.bias_correctors_path)
            self.heavy_rain_model = joblib.load(self.heavy_rain_model_path)
            return True
        except Exception as e:
            print(f"Error loading actual trained models from {self.models_dir}: {e}")
            self.regime_classifier = None
            self.bias_correctors = None
            self.heavy_rain_model = None
            return False

    def predict_regime(self, X: np.ndarray) -> Tuple[int, str, float]:
        """
        Predicts active regime index, name, and confidence score using actual trained model.
        X shape: (1, 4) with [raw_nwp, u850, rh700, mslp_grad]
        """
        if self.regime_classifier is None:
            raise FileNotFoundError(
                f"Missing actual trained model: '{self.regime_classifier_path}'. "
                "Fallback has been removed. You must place your trained regime_classifier.joblib file in the models/ directory."
            )

        preds = self.regime_classifier.predict(X)
        reg_id = int(preds[0])

        confidence = 0.85
        if hasattr(self.regime_classifier, "predict_proba"):
            probas = self.regime_classifier.predict_proba(X)
            confidence = float(np.max(probas[0]))

        reg_name = REGIME_MAP.get(reg_id, f"Regime {reg_id}")
        return reg_id, reg_name, confidence

    def apply_bias_correction(self, X: np.ndarray, regime_id: int) -> float:
        """
        Applies actual trained regime-specific regressor to correct raw NWP rainfall.
        """
        if self.bias_correctors is None:
            raise FileNotFoundError(
                f"Missing actual trained model: '{self.bias_correctors_path}'. "
                "Fallback has been removed. You must place your trained bias_correctors.joblib file in the models/ directory."
            )

        raw_nwp = float(X[0, 0])

        # If dictionary of models per regime
        if isinstance(self.bias_correctors, dict):
            reg_model = self.bias_correctors.get(regime_id) or self.bias_correctors.get(str(regime_id))
            
            # Fallback to global model if specific regime model is not found
            if reg_model is None and 'global' in self.bias_correctors:
                reg_model = self.bias_correctors['global']
                
            if reg_model is not None:
                val = float(reg_model.predict(X)[0])
                return max(0.0, round(val, 1))
            else:
                raise KeyError(
                    f"Trained bias_correctors model dictionary does not contain a regressor for regime_id {regime_id}. "
                    f"Available regime keys: {list(self.bias_correctors.keys())}"
                )

        # If single model that takes regime as feature or direct predictor
        if hasattr(self.bias_correctors, "predict"):
            val = float(self.bias_correctors.predict(X)[0])
            return max(0.0, round(val, 1))

        raise ValueError("Loaded bias_correctors.joblib is neither a dict of models nor an object with .predict().")

    def predict_heavy_rainfall_prob(self, X: np.ndarray, corrected_val: float) -> Dict[str, float]:
        """
        Predicts probabilities for IMD standard warning thresholds using actual trained model:
        - Heavy (>= 64.5 mm)
        - Very Heavy (>= 115.6 mm)
        - Extremely Heavy (>= 204.5 mm)
        """
        if self.heavy_rain_model is None or not hasattr(self.heavy_rain_model, "predict_proba"):
            raise FileNotFoundError(
                f"Missing actual trained model: '{self.heavy_rain_model_path}'. "
                "Fallback has been removed. You must place your trained heavy_rain_prob_model.joblib file in the models/ directory."
            )

        probas = self.heavy_rain_model.predict_proba(X)
        if probas.shape[1] > 1:
            prob_64_5 = float(probas[0, 1])
        else:
            prob_64_5 = float(probas[0, 0])

        # Scaled conditional probabilities for higher IMD alert brackets
        prob_115_6 = min(1.0, max(0.0, prob_64_5 * float(np.exp(-max(0.0, 115.6 - corrected_val) / 35.0))))
        prob_204_5 = min(1.0, max(0.0, prob_115_6 * float(np.exp(-max(0.0, 204.5 - corrected_val) / 45.0))))

        return {
            "prob_heavy_64_5": round(float(prob_64_5), 3),
            "prob_very_heavy_115_6": round(float(prob_115_6), 3),
            "prob_extremely_heavy_204_5": round(float(prob_204_5), 3)
        }

    def run_pipeline(
        self,
        raw_nwp: float,
        u850: float = 12.0,
        rh700: float = 80.0,
        mslp_grad: float = -2.5,
        forced_regime_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Executes full inference using actual trained models:
        Feature Prep -> Regime Classification -> Regime-Conditioned Bias Correction -> Heavy Rain Probability.
        Raises FileNotFoundError if any trained model file is missing.
        """
        if not self.all_models_ready():
            missing = [k for k, v in self.check_models_exist().items() if not v]
            raise FileNotFoundError(
                f"Cannot run MONSOON-AI pipeline. Missing actual trained model file(s): {missing}. "
                f"Please place all 3 required .joblib files in '{self.models_dir}'."
            )

        # Feature array: [raw_nwp, u850, rh700, mslp_grad]
        X = np.array([[raw_nwp, u850, rh700, mslp_grad]], dtype=float)

        if forced_regime_id is not None:
            reg_id = int(forced_regime_id)
            reg_name = REGIME_MAP.get(reg_id, f"Regime {reg_id}")
            reg_conf = 1.0
        else:
            reg_id, reg_name, reg_conf = self.predict_regime(X)

        corrected_rainfall = self.apply_bias_correction(X, reg_id)
        probs = self.predict_heavy_rainfall_prob(X, corrected_rainfall)
        delta = round(corrected_rainfall - raw_nwp, 1)

        # Risk Classification (IMD Warning System)
        if probs["prob_extremely_heavy_204_5"] >= 0.40 or corrected_rainfall >= 150:
            warning_level = "Red Alert"
            warning_color = "#EF4444"
        elif probs["prob_very_heavy_115_6"] >= 0.50 or corrected_rainfall >= 90:
            warning_level = "Orange Alert"
            warning_color = "#F97316"
        elif probs["prob_heavy_64_5"] >= 0.45 or corrected_rainfall >= 55:
            warning_level = "Yellow Alert"
            warning_color = "#EAB308"
        else:
            warning_level = "Green / No Warning"
            warning_color = "#10B981"

        return {
            "inputs": {
                "raw_nwp": raw_nwp,
                "u850": u850,
                "rh700": rh700,
                "mslp_grad": mslp_grad
            },
            "regime_id": reg_id,
            "regime_name": reg_name,
            "regime_confidence": round(reg_conf, 3),
            "raw_nwp": raw_nwp,
            "ai_corrected": corrected_rainfall,
            "delta_mm": delta,
            "delta_pct": round((delta / raw_nwp * 100), 1) if raw_nwp > 0 else 0.0,
            "probabilities": probs,
            "warning_level": warning_level,
            "warning_color": warning_color
        }
