"""
Page 3: Regime & AI Explanation (Core USP)
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

st.set_page_config(page_title="Regime & AI Explanation | MONSOON-AI", page_icon="🧠", layout="wide")

from utils.ui import apply_custom_theme, render_sidebar, animated_metric, svg_spinner
apply_custom_theme()
render_sidebar()

st.markdown("""
<style>
    .stApp { background-color: #0B1220; color: #F1F5F9; }
    .pipeline-step {
        background: #111B2E;
        border: 1px solid #1E2E4A;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .pipeline-arrow {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        color: #38BDF8;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧠 Regime & AI Explanation Engine (Core USP)")
st.markdown(
    "Understanding the physical and meteorological reasons behind AI bias corrections. "
    "*(SIH26080: Solving regime-dependent NWP forecast errors)*"
)

engine = MonsoonInferenceEngine(root_dir / "models")

if not engine.all_models_ready():
    missing = [k for k, v in engine.check_models_exist().items() if not v]
    st.error(
        f"🚨 **Actual Trained Models Required**\n\n"
        f"Missing model files: `{', '.join(missing)}` in `{root_dir / 'models'}`.\n\n"
        "Synthetic fallbacks have been removed in strict mode. Please place your trained `.joblib` files in the `models/` directory or upload them on the home page."
    )
    st.stop()

# Pipeline Flow Diagram (Visual Step-by-Step)
st.subheader("🔄 End-to-End Regime-Conditioned Architecture")
p1, a1, p2, a2, p3, a3, p4 = st.columns([2, 0.5, 2, 0.5, 2, 0.5, 2])

with p1:
    st.markdown("""
    <div class="pipeline-step">
        <h5 style="color:#94A3B8; margin:0;">Stage 1: NWP & Atmosphere</h5>
        <h3 style="color:#38BDF8; margin:6px 0;">4 Key Features</h3>
        <p style="font-size:0.8rem; margin:0; color:#CBD5E1;">Raw Rain, u850, rh700, MSLP Gradient</p>
    </div>
    """, unsafe_allow_html=True)

with a1:
    st.markdown('<div class="pipeline-arrow">➔</div>', unsafe_allow_html=True)

with p2:
    st.markdown("""
    <div class="pipeline-step">
        <h5 style="color:#94A3B8; margin:0;">Stage 2: Synoptic Engine</h5>
        <h3 style="color:#F59E0B; margin:6px 0;">Regime Classifier</h3>
        <p style="font-size:0.8rem; margin:0; color:#CBD5E1;">Active / Break / LPS / Offshore / Normal</p>
    </div>
    """, unsafe_allow_html=True)

with a2:
    st.markdown('<div class="pipeline-arrow">➔</div>', unsafe_allow_html=True)

with p3:
    st.markdown("""
    <div class="pipeline-step">
        <h5 style="color:#94A3B8; margin:0;">Stage 3: Conditional ML</h5>
        <h3 style="color:#10B981; margin:6px 0;">Bias Correctors</h3>
        <p style="font-size:0.8rem; margin:0; color:#CBD5E1;">Dedicated Regressor for Active Regime</p>
    </div>
    """, unsafe_allow_html=True)

with a3:
    st.markdown('<div class="pipeline-arrow">➔</div>', unsafe_allow_html=True)

with p4:
    st.markdown("""
    <div class="pipeline-step">
        <h5 style="color:#94A3B8; margin:0;">Stage 4: Operational Alert</h5>
        <h3 style="color:#EC4899; margin:6px 0;">Risk Probabilities</h3>
        <p style="font-size:0.8rem; margin:0; color:#CBD5E1;">P(≥64.5mm), P(≥115.6mm), P(≥204.5mm)</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Interactive Diagnostic Playground
st.subheader("🔬 Synoptic Case Study & LLM Reasoning")
col_inp, col_out = st.columns([1, 1])

with col_inp:
    st.markdown("##### 1. Select / Configure Synoptic State")
    regime_case = st.selectbox(
        "Synoptic Weather Preset",
        options=[
            "Break Monsoon: High NWP wet bias over Central India",
            "Active Monsoon: NWP underpredicting Western Ghats / Trough core",
            "Monsoon Depression (Bay of Bengal): Heavy Rain & Track shift",
            "Offshore Trough: Severe Konkan/Goa Coastal Surge",
            "Normal / Transition: Convective afternoon drizzle"
        ],
        index=0
    )

    if "Break Monsoon" in regime_case:
        default_nwp = 58.0
        default_u850 = 3.5
        default_rh700 = 62.0
        default_mslp = 2.1
        reg_id = 2
        region = "Vidarbha / Nagpur (Central India)"
    elif "Active Monsoon" in regime_case:
        default_nwp = 42.0
        default_u850 = 16.5
        default_rh700 = 84.0
        default_mslp = -2.8
        reg_id = 1
        region = "Western Ghats / Mahabaleshwar"
    elif "Depression" in regime_case:
        default_nwp = 65.0
        default_u850 = 18.0
        default_rh700 = 92.0
        default_mslp = -6.2
        reg_id = 3
        region = "Odisha & Chhattisgarh Coastal Belt"
    elif "Offshore" in regime_case:
        default_nwp = 55.0
        default_u850 = 14.0
        default_rh700 = 88.0
        default_mslp = -3.5
        reg_id = 4
        region = "Mumbai / Konkan Coast"
    else:
        default_nwp = 22.0
        default_u850 = 8.0
        default_rh700 = 70.0
        default_mslp = -0.5
        reg_id = 0
        region = "Deccan Plateau / Telangana"

    val_nwp = st.slider("Raw NWP Rainfall Forecast (mm)", 0.0, 200.0, float(default_nwp), 0.5)
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        val_u850 = st.slider("850 hPa Zonal Wind (m/s)", -10.0, 30.0, float(default_u850), 0.5)
        val_rh700 = st.slider("700 hPa Relative Humidity (%)", 30.0, 100.0, float(default_rh700), 1.0)
    with c_f2:
        val_mslp = st.slider("MSLP Gradient Anomaly (hPa)", -15.0, 10.0, float(default_mslp), 0.5)
        selected_region = st.text_input("Region / Meteorological Subdivision", value=region)

    run_btn = st.button("🚀 Run AI Pipeline & Generate LLM Explanation", use_container_width=True)

with col_out:
    st.markdown("##### 2. AI Post-Processing Results")
    res = engine.run_pipeline(
        raw_nwp=val_nwp,
        u850=val_u850,
        rh700=val_rh700,
        mslp_grad=val_mslp,
        forced_regime_id=reg_id
    )

    m1, m2, m3 = st.columns(3)
    with m1:
        animated_metric("Raw NWP Forecast", res['raw_nwp'], suffix=" mm")
    with m2:
        animated_metric(
            "AI Corrected Forecast",
            res['ai_corrected'],
            suffix=" mm",
            delta=f"{res['delta_mm']:+} mm"
        )
    with m3:
        animated_metric("Identified Regime", res['regime_name'].split('/')[0], delta=f"Conf: {res['regime_confidence']*100:.0f}%")

    # Before vs After Radar/Bar Comparison
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Raw NWP", "AI Corrected"],
        y=[res['raw_nwp'], res['ai_corrected']],
        marker_color=["#64748B", "#38BDF8"],
        text=[f"{res['raw_nwp']} mm", f"{res['ai_corrected']} mm"],
        textposition="auto"
    ))
    fig.update_layout(
        title="Before vs After Forecast Adjustment",
        paper_bgcolor="#0B1220",
        plot_bgcolor="#111B2E",
        font=dict(color="#E2E8F0"),
        height=220,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# LLM Explanation Section
st.subheader("🤖 Why AI Changed the Forecast (Powered by LLM)")
groq_key = st.session_state.get("groq_key", "")

if run_btn:
    with svg_spinner(root_dir / "animations" / "loading.svg", "Generating expert synoptic rationale..."):
        explanation = explain_forecast_adjustment(
            regime_name=res['regime_name'],
            raw_nwp=res['raw_nwp'],
            ai_corrected=res['ai_corrected'],
            heavy_rain_prob=res['probabilities']['prob_heavy_64_5'],
            district_or_region=selected_region,
            features={"u850": val_u850, "rh700": val_rh700, "mslp_grad": val_mslp},
            groq_key=groq_key
        )

    st.markdown(f"""
    <div style="background: #111B2E; border-left: 4px solid #38BDF8; padding: 18px 22px; border-radius: 8px;">
        {explanation}
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Click 'Run AI Pipeline & Generate LLM Explanation' to generate the diagnostic rationale.")
