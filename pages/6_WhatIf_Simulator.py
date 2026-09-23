"""
Page 6: What-If Simulator
MONSOON-AI: Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from utils.inference import MonsoonInferenceEngine, REGIME_MAP
from utils.llm_explainer import explain_forecast_adjustment, get_llm_client

st.set_page_config(page_title="What-If Simulator | MONSOON-AI", page_icon="⚡", layout="wide")

from utils.ui import apply_custom_theme, render_sidebar
apply_custom_theme()
render_sidebar()

st.markdown("""
<style>
    .stApp { background-color: #0B1220; color: #F1F5F9; }
    .sim-card {
        background: #111B2E;
        border: 1px solid #1E2E4A;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .res-metric {
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.1;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Meteorological What-If Simulator")
st.markdown("Interactively experiment with atmospheric synoptic forcing and evaluate how the AI model responds.")

engine = MonsoonInferenceEngine(root_dir / "models")

if not engine.all_models_ready():
    missing = [k for k, v in engine.check_models_exist().items() if not v]
    st.error(
        f"🚨 **Actual Trained Models Required**\n\n"
        f"Missing model files: `{', '.join(missing)}` in `{root_dir / 'models'}`.\n\n"
        "Synthetic fallbacks have been removed in strict mode. Please place your trained `.joblib` files in the `models/` directory or upload them on the home page."
    )
    st.stop()

# Preset buttons for quick scenario loading
st.markdown("##### 🎯 Quick Scenario Presets")
cp1, cp2, cp3, cp4 = st.columns(4)

scenario = None
with cp1:
    if st.button("🌦️ Break Regime False Alarm", use_container_width=True):
        scenario = {
            "regime": "Break Monsoon",
            "nwp": 64.0,
            "u850": 3.2,
            "rh700": 58.0,
            "mslp": 2.5,
            "loc": "Nagpur / Vidarbha Plains"
        }
with cp2:
    if st.button("🌊 Ghats Orographic Deluge", use_container_width=True):
        scenario = {
            "regime": "Offshore Trough / Convective Surge",
            "nwp": 52.0,
            "u850": 17.5,
            "rh700": 94.0,
            "mslp": -3.8,
            "loc": "Mahabaleshwar / Konkan"
        }
with cp3:
    if st.button("🌀 Bay Monsoon Depression", use_container_width=True):
        scenario = {
            "regime": "Monsoon Depression / LPS",
            "nwp": 75.0,
            "u850": 21.0,
            "rh700": 96.0,
            "mslp": -7.5,
            "loc": "Bhubaneswar / Coastal Odisha"
        }
with cp4:
    if st.button("☀️ Normal Monsoon Day", use_container_width=True):
        scenario = {
            "regime": "Normal / Transition",
            "nwp": 18.0,
            "u850": 9.0,
            "rh700": 68.0,
            "mslp": -0.5,
            "loc": "Hyderabad / Telangana"
        }

# User Controls
col_ctrl, col_res = st.columns([1, 1])

with col_ctrl:
    st.markdown("### 🎛️ Atmospheric & Forecast Inputs")

    regimes_list = [
        "Active Monsoon",
        "Break Monsoon",
        "Monsoon Depression / LPS",
        "Offshore Trough / Convective Surge",
        "Normal / Transition"
    ]

    selected_regime = st.selectbox(
        "Synoptic Regime",
        options=regimes_list,
        index=regimes_list.index(scenario["regime"]) if scenario else 0
    )

    nwp_input = st.slider(
        "Raw NWP Forecast Rainfall (mm/24h)",
        min_value=0.0,
        max_value=250.0,
        value=float(scenario["nwp"]) if scenario else 45.0,
        step=1.0,
        help="Deterministic forecast from numerical model (GFS/NCUM)"
    )

    c_w1, c_w2 = st.columns(2)
    with c_w1:
        u850_input = st.slider(
            "850 hPa Zonal Wind u850 (m/s)",
            -15.0, 35.0,
            float(scenario["u850"]) if scenario else 12.0,
            0.5,
            help="Low-level monsoon westerlies / Somali Jet speed"
        )
        rh700_input = st.slider(
            "700 hPa Relative Humidity (%)",
            20.0, 100.0,
            float(scenario["rh700"]) if scenario else 82.0,
            1.0,
            help="Middle-tropospheric moisture content"
        )

    with c_w2:
        mslp_input = st.slider(
            "MSLP Gradient / Anomaly (hPa)",
            -15.0, 10.0,
            float(scenario["mslp"]) if scenario else -2.5,
            0.5,
            help="Pressure deficit indicative of cyclonic vortex"
        )
        location_input = st.text_input(
            "Target Location / District",
            value=scenario["loc"] if scenario else "Central India / Vidarbha"
        )

    run_sim = st.button("🚀 Run AI Correction", use_container_width=True)

# Map regime name to ID
regime_to_id = {v: k for k, v in REGIME_MAP.items()}
reg_id = regime_to_id.get(selected_regime, 0)

with col_res:
    st.markdown("### 📊 AI Model Output & Risk Profile")

    output = engine.run_pipeline(
        raw_nwp=nwp_input,
        u850=u850_input,
        rh700=rh700_input,
        mslp_grad=mslp_input,
        forced_regime_id=reg_id
    )

    delta = output["delta_mm"]
    delta_color = "#38BDF8" if delta > 0 else ("#EF4444" if delta < 0 else "#94A3B8")

    st.markdown(f"""
    <div class="sim-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="color:#94A3B8; font-size:0.85rem; font-weight:600;">AI-CORRECTED RAINFALL</div>
                <div class="res-metric" style="color:#38BDF8;">{output['ai_corrected']} mm</div>
                <div style="color:{delta_color}; font-size:0.9rem; font-weight:600;">
                    {delta:+} mm ({output['delta_pct']:+}%) adjustment vs Raw NWP
                </div>
            </div>
            <div style="text-align:right;">
                <div style="color:#94A3B8; font-size:0.85rem; font-weight:600;">RAW NWP FORECAST</div>
                <div class="res-metric" style="color:#94A3B8; font-size:1.6rem;">{output['raw_nwp']} mm</div>
                <div style="color:{output['warning_color']}; font-weight:bold; font-size:0.95rem; margin-top:4px;">
                    {output['warning_level']}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Extreme probabilities gauge/bar
    st.markdown("##### 🌧️ Calibrated Rainfall Exceedance Probabilities")
    probs = output["probabilities"]
    
    pr1, pr2, pr3 = st.columns(3)
    with pr1:
        st.metric("P(Rain ≥ 64.5 mm)", f"{probs['prob_heavy_64_5']*100:.1f}%", "Heavy Rain")
    with pr2:
        st.metric("P(Rain ≥ 115.6 mm)", f"{probs['prob_very_heavy_115_6']*100:.1f}%", "Very Heavy")
    with pr3:
        st.metric("P(Rain ≥ 204.5 mm)", f"{probs['prob_extremely_heavy_204_5']*100:.1f}%", "Extremely Heavy")

    # Bar visualization
    fig_b = go.Figure()
    fig_b.add_trace(go.Bar(
        x=["Raw NWP", "AI Corrected"],
        y=[output["raw_nwp"], output["ai_corrected"]],
        marker_color=["#64748B", "#0284C7"],
        text=[f"{output['raw_nwp']} mm", f"{output['ai_corrected']} mm"],
        textposition="auto"
    ))
    fig_b.update_layout(
        paper_bgcolor="#0B1220",
        plot_bgcolor="#111B2E",
        font=dict(color="#E2E8F0"),
        height=190,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_b, use_container_width=True)

st.markdown("---")

# LLM Explanation Section
st.subheader("🧠 Synoptic Physical Rationale (AI Explainer)")
with st.spinner("Consulting Meteorological LLM Engine..."):
    explanation = explain_forecast_adjustment(
        regime_name=selected_regime,
        raw_nwp=output["raw_nwp"],
        ai_corrected=output["ai_corrected"],
        heavy_rain_prob=probs["prob_heavy_64_5"],
        district_or_region=location_input,
        features={
            "u850": u850_input,
            "rh700": rh700_input,
            "mslp_grad": mslp_input
        },
        groq_key=st.session_state.get("groq_key", "")
    )

st.markdown(f"""
<div style="background: #111B2E; border-left: 4px solid #38BDF8; padding: 18px 22px; border-radius: 8px;">
    {explanation}
</div>
""", unsafe_allow_html=True)
