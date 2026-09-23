"""
MONSOON-AI Verification Metrics Module
Calculates standard WMO/IMD meteorological verification scores for continuous and categorical rainfall.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional


def calculate_continuous_metrics(obs: np.ndarray, pred: np.ndarray) -> Dict[str, float]:
    """
    Calculate continuous forecast verification metrics:
    RMSE, MAE, Mean Bias, Pearson Correlation, and Skill Score.
    """
    mask = ~np.isnan(obs) & ~np.isnan(pred)
    y_true = np.asarray(obs[mask], dtype=float)
    y_pred = np.asarray(pred[mask], dtype=float)

    if len(y_true) == 0:
        return {
            "RMSE": 0.0,
            "MAE": 0.0,
            "Mean_Bias": 0.0,
            "Correlation": 0.0,
            "Count": 0
        }

    # Mean Absolute Error
    mae = float(np.mean(np.abs(y_pred - y_true)))

    # Root Mean Square Error
    rmse = float(np.sqrt(np.mean((y_pred - y_true) ** 2)))

    # Mean Bias
    mean_bias = float(np.mean(y_pred - y_true))

    # Pearson Correlation Coefficient
    if np.std(y_true) > 1e-6 and np.std(y_pred) > 1e-6:
        corr = float(np.corrcoef(y_true, y_pred)[0, 1])
    else:
        corr = 0.0

    return {
        "RMSE": round(rmse, 2),
        "MAE": round(mae, 2),
        "Mean_Bias": round(mean_bias, 2),
        "Correlation": round(corr, 3),
        "Count": int(len(y_true))
    }


def calculate_contingency_table(obs: np.ndarray, pred: np.ndarray, threshold: float = 64.5) -> Tuple[int, int, int, int]:
    """
    Compute 2x2 contingency table (Hits, False Alarms, Misses, Correct Negatives)
    for a given threshold (e.g., IMD Heavy Rain >= 64.5 mm).
    """
    mask = ~np.isnan(obs) & ~np.isnan(pred)
    y_true = np.asarray(obs[mask] >= threshold, dtype=bool)
    y_pred = np.asarray(pred[mask] >= threshold, dtype=bool)

    hits = int(np.sum(y_true & y_pred))
    false_alarms = int(np.sum(~y_true & y_pred))
    misses = int(np.sum(y_true & ~y_pred))
    correct_negatives = int(np.sum(~y_true & ~y_pred))

    return hits, false_alarms, misses, correct_negatives


def calculate_categorical_scores(hits: int, false_alarms: int, misses: int, correct_negatives: int) -> Dict[str, float]:
    """
    Calculate standard categorical forecast scores:
    POD (Probability of Detection / Hit Rate)
    FAR (False Alarm Ratio)
    CSI (Critical Success Index / Threat Score)
    ETS (Equitable Threat Score)
    BIAS (Frequency Bias)
    """
    total = hits + false_alarms + misses + correct_negatives
    if total == 0:
        return {"POD": 0.0, "FAR": 0.0, "CSI": 0.0, "ETS": 0.0, "BIAS": 1.0}

    # POD: Hits / (Hits + Misses)
    observed_events = hits + misses
    pod = hits / observed_events if observed_events > 0 else 0.0

    # FAR: False Alarms / (Hits + False Alarms)
    forecast_events = hits + false_alarms
    far = false_alarms / forecast_events if forecast_events > 0 else 0.0

    # CSI: Hits / (Hits + Misses + False Alarms)
    denom_csi = hits + misses + false_alarms
    csi = hits / denom_csi if denom_csi > 0 else 0.0

    # Frequency Bias: Forecast / Observed
    bias = forecast_events / observed_events if observed_events > 0 else 1.0

    # ETS: (Hits - Hits_random) / (Hits + Misses + False Alarms - Hits_random)
    hits_random = (forecast_events * observed_events) / total if total > 0 else 0.0
    denom_ets = denom_csi - hits_random
    ets = (hits - hits_random) / denom_ets if denom_ets > 0 else 0.0

    return {
        "POD": round(pod, 3),
        "FAR": round(far, 3),
        "CSI": round(csi, 3),
        "ETS": round(ets, 3),
        "BIAS": round(bias, 2),
        "Hits": hits,
        "False_Alarms": false_alarms,
        "Misses": misses,
        "Correct_Negatives": correct_negatives
    }


def compare_models_metrics(
    obs: np.ndarray,
    nwp: np.ndarray,
    ai_corrected: np.ndarray,
    threshold: float = 64.5
) -> Dict[str, Any]:
    """
    Compute full side-by-side comparison between Raw NWP and AI-Corrected forecasts.
    """
    nwp_cont = calculate_continuous_metrics(obs, nwp)
    ai_cont = calculate_continuous_metrics(obs, ai_corrected)

    nwp_tbl = calculate_contingency_table(obs, nwp, threshold)
    ai_tbl = calculate_contingency_table(obs, ai_corrected, threshold)

    nwp_cat = calculate_categorical_scores(*nwp_tbl)
    ai_cat = calculate_categorical_scores(*ai_tbl)

    # Calculate Improvement %
    rmse_improvement = (
        ((nwp_cont["RMSE"] - ai_cont["RMSE"]) / nwp_cont["RMSE"] * 100)
        if nwp_cont["RMSE"] > 0 else 0.0
    )
    mae_improvement = (
        ((nwp_cont["MAE"] - ai_cont["MAE"]) / nwp_cont["MAE"] * 100)
        if nwp_cont["MAE"] > 0 else 0.0
    )
    far_reduction = (
        ((nwp_cat["FAR"] - ai_cat["FAR"]) / nwp_cat["FAR"] * 100)
        if nwp_cat["FAR"] > 0 else 0.0
    )
    csi_gain = (
        ((ai_cat["CSI"] - nwp_cat["CSI"]) / (nwp_cat["CSI"] + 1e-4) * 100)
        if nwp_cat["CSI"] > 0 else 0.0
    )

    return {
        "continuous": {
            "NWP": nwp_cont,
            "AI_Corrected": ai_cont,
            "RMSE_Improvement_Pct": round(rmse_improvement, 1),
            "MAE_Improvement_Pct": round(mae_improvement, 1)
        },
        "categorical": {
            "Threshold_mm": threshold,
            "NWP": nwp_cat,
            "AI_Corrected": ai_cat,
            "FAR_Reduction_Pct": round(far_reduction, 1),
            "CSI_Gain_Pct": round(csi_gain, 1)
        }
    }


def compute_regime_wise_metrics(
    df: pd.DataFrame,
    obs_col: str = "obs_rainfall",
    nwp_col: str = "raw_nwp",
    ai_col: str = "ai_corrected",
    regime_col: str = "regime_name"
) -> pd.DataFrame:
    """
    Computes performance metrics stratified across distinct monsoon regimes.
    """
    regimes = df[regime_col].unique()
    records = []

    for reg in regimes:
        sub = df[df[regime_col] == reg]
        if len(sub) == 0:
            continue

        obs = sub[obs_col].values
        nwp = sub[nwp_col].values
        ai = sub[ai_col].values

        nwp_cont = calculate_continuous_metrics(obs, nwp)
        ai_cont = calculate_continuous_metrics(obs, ai)

        nwp_tbl = calculate_contingency_table(obs, nwp, threshold=64.5)
        ai_tbl = calculate_contingency_table(obs, ai, threshold=64.5)

        nwp_cat = calculate_categorical_scores(*nwp_tbl)
        ai_cat = calculate_categorical_scores(*ai_tbl)

        rmse_imp = (
            ((nwp_cont["RMSE"] - ai_cont["RMSE"]) / nwp_cont["RMSE"] * 100)
            if nwp_cont["RMSE"] > 0 else 0.0
        )

        records.append({
            "Regime": reg,
            "Sample Count": len(sub),
            "NWP RMSE (mm)": nwp_cont["RMSE"],
            "AI RMSE (mm)": ai_cont["RMSE"],
            "RMSE Reduction (%)": round(rmse_imp, 1),
            "NWP MAE (mm)": nwp_cont["MAE"],
            "AI MAE (mm)": ai_cont["MAE"],
            "NWP CSI": nwp_cat["CSI"],
            "AI CSI": ai_cat["CSI"],
            "NWP FAR": nwp_cat["FAR"],
            "AI FAR": ai_cat["FAR"]
        })

    return pd.DataFrame(records)
