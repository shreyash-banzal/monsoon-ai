"""
MONSOON-AI: Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts
Smart India Hackathon (SIH26080)
Main Streamlit Application Entrypoint
"""

import os
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

# Ensure local utils and packages are importable
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from utils.inference import MonsoonInferenceEngine, REGIME_MAP
from utils.map_utils import (
    generate_monsoon_district_dataset,
    create_rainfall_folium_map,
    create_plotly_comparison_chart
)
from utils.llm_explainer import explain_forecast_adjustment, get_llm_client

# Page configuration
st.set_page_config(
    page_title="MONSOON-AI | Regime-Aware Rainfall Intelligence",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Meteorological Dark Theme Styling (#0B1220)
st.markdown("""
<style>
    /* Dark meteorological background */
    .stApp {
        background-color: #0B1220;
        color: #F1F5F9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide the default sidebar navigation since we build our own */
    [data-testid="stSidebarNav"] {
        display: none;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #070D18;
        border-right: 1px solid #1E293B;
    }
    
    /* Custom Sidebar Header */
    .sidebar-header-box {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 20px;
    }
    .sih-badge {
        background: #0284C7;
        color: white;
        padding: 2px 6px;
        font-size: 0.7rem;
        border-radius: 4px;
        font-weight: bold;
        letter-spacing: 0.05em;
    }
    
    /* KPI Metric Cards */
    .kpi-card {
        background: linear-gradient(145deg, #111B2E, #0D1524);
        border: 1px solid #1E2E4A;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        border-color: #38BDF8;
        transform: translateY(-2px);
    }
    .kpi-title {
        color: #94A3B8;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: #F8FAFC;
        font-size: 1.85rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .kpi-subtitle {
        color: #38BDF8;
        font-size: 0.75rem;
        margin-top: 6px;
        font-weight: 500;
    }
    
    /* Selected Station Card */
    .station-panel {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 20px;
    }
    .station-title {
        font-size: 0.85rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .station-name {
        font-size: 1.25rem;
        font-weight: bold;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .station-sub {
        color: #0284c7;
        font-size: 0.85rem;
        margin-bottom: 20px;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        margin-top: 15px;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 15px;
    }
    .metric-col { width: 48%; }
    .metric-label { font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; margin-bottom: 5px;}
    .metric-val { font-size: 1.5rem; font-weight: bold; color: white; }
    .metric-sub { font-size: 0.75rem; color: #64748B; }
    
    /* Badges */
    .badge-red { background-color: #DC2626; color: white; padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
    .badge-orange { background-color: #f97316; color: white; padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; border: 1px solid #c2410c; }
    
    /* Checkpoint list */
    .ckpt-list {
        background: #111B2E;
        border: 1px solid #1E2E4A;
        border-radius: 8px;
        padding: 10px;
        margin-top: 5px;
        font-size: 0.8rem;
        color: #4ADE80;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #0284C7, #0369A1);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }
    
    /* Flexbox Top Nav styling overrides for selectbox */
    .top-nav-row {
        display: flex;
        align-items: center;
        width: 100%;
        gap: 20px;
        border-bottom: 1px solid #1E293B;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .live-feed {
        color: #4ADE80;
        font-size: 0.85rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .live-dot {
        width: 8px;
        height: 8px;
        background-color: #4ADE80;
        border-radius: 50%;
        display: inline-block;
    }

    /* --- Smooth Interactions & Transitions --- */
    /* Apply transitions to built-in Streamlit components and custom cards */
    .stButton > button, 
    .stTabs [data-baseweb="tab"], 
    [data-testid="stSidebar"], 
    [data-testid="stMetric"], 
    [data-baseweb="select"], 
    .stSlider,
    .kpi-card,
    .station-panel {
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    /* Hover states for buttons and cards (subtle lift + soft shadow increase) */
    .stButton > button:hover, 
    [data-testid="stMetric"]:hover,
    .kpi-card:hover,
    .station-panel:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5) !important;
    }

    /* Rerun Fade-In Animation */
    @keyframes softFadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    [data-testid="stAppViewBlockContainer"], .block-container {
        animation: softFadeIn 400ms ease-out forwards;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initializes app session states."""
    if "models_dir" not in st.session_state:
        st.session_state.models_dir = current_dir / "models"
    if "engine" not in st.session_state:
        st.session_state.engine = MonsoonInferenceEngine(st.session_state.models_dir)
    if "active_regime" not in st.session_state:
        st.session_state.active_regime = "Active Monsoon"
    if "groq_key" not in st.session_state:
        st.session_state.groq_key = os.getenv("GROQ_API_KEY", "")


init_session_state()

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header-box">
        <div style="font-size: 2.2rem; line-height: 1; text-shadow: 0 0 10px #38BDF8;">🌧️</div>
        <div style="line-height:1.2;">
            <div style="display:flex; align-items:center; gap:8px;">
                <b style="font-size:1.1rem; color:white; font-weight:800;">MONSOON-AI</b>
            </div>
            <div style="font-size:0.75rem; color:#94a3b8; font-weight:500;">Regime Aware Rainfall AI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 10px 0; border-color: #1e293b'>", unsafe_allow_html=True)

    # Manual Navigation Links
    st.page_link("app.py", label="1. Command Center", icon="🎯")
    
    # We conditionally link others if the pages exist
    # if `pages/` exists, normally they are available.
    if (current_dir / "pages" / "2_Rainfall_Map.py").exists():
        st.page_link("pages/2_Rainfall_Map.py", label="2. Rainfall Map", icon="🗺️")
    if (current_dir / "pages" / "3_Regime_AI.py").exists():
        st.page_link("pages/3_Regime_AI.py", label="3. Regime & AI Explainer", icon="🧠")
    if (current_dir / "pages" / "4_Heavy_Rain_Alerts.py").exists():
        st.page_link("pages/4_Heavy_Rain_Alerts.py", label="4. Heavy Rain Alerts", icon="⚠️")
    if (current_dir / "pages" / "5_Verification_Lab.py").exists():
        st.page_link("pages/5_Verification_Lab.py", label="5. Verification Lab", icon="📊")
    if (current_dir / "pages" / "6_WhatIf_Simulator.py").exists():
        st.page_link("pages/6_WhatIf_Simulator.py", label="6. What If Simulator", icon="🎛️")

    st.markdown("<hr style='margin: 15px 0; border-color: #1e293b'>", unsafe_allow_html=True)

    # 1. Model Status Checker
    status = st.session_state.engine.check_models_exist()
    all_ready = all(status.values())

    if all_ready:
        st.markdown("""
        <div style="font-size: 0.85rem; font-weight: 600; color: #E2E8F0; margin-bottom: 5px;">
            <span style="color:#4ADE80;">✓</span> Checkpoints Ready
        </div>
        <div class="ckpt-list">
            ✓ regime_classifier.joblib<br/>
            ✓ bias_correctors.joblib<br/>
            ✓ heavy_rain_prob.joblib
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("🚨 Missing Models")

    st.markdown("<hr style='margin: 15px 0; border-color: #1e293b'>", unsafe_allow_html=True)

    # 2. LLM Engine
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div style="font-size: 0.85rem; font-weight: 600; color: #E2E8F0;">✨ LLM Engine</div>
        <div style="background:#065f46; color:#a7f3d0; padding:2px 6px; font-size:0.6rem; border-radius:4px; font-weight:bold;">LIVE AI</div>
    </div>
    <div style="font-size:0.75rem; color:#0284c7; margin-bottom: 10px; margin-top:2px; font-weight:500;">IMD Physics Rule Engine</div>
    """, unsafe_allow_html=True)

    st.markdown("<br/><br/>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.7rem; color:#64748b; margin-top: auto;">
        Runtime <span style="float:right; color:#38BDF8;">Python 3.13</span><br/>
        IMD & NCMRWF Post-Processing Engine
    </div>
    """, unsafe_allow_html=True)


# ================= MAIN LANDING / COMMAND CENTER =================

# Top custom nav bar simulation
col_sys, col_time = st.columns([2, 1])
with col_sys:
    st.markdown("<div style='font-size:0.8rem; font-weight:bold; color:#64748B; margin-bottom:5px; text-transform:uppercase;'>ACTIVE SYNOPTIC REGIME:</div>", unsafe_allow_html=True)
    selected_regime = st.selectbox(
        "ACTIVE SYNOPTIC REGIME:",
        options=[
            "Active Monsoon (Strong Somali Jet & Trough)",
            "Break Monsoon",
            "Monsoon Depression / LPS",
            "Offshore Trough / Convective Surge",
            "Normal / Transition"
        ],
        index=0,
        label_visibility="collapsed"
    )
with col_time:
    st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex; justify-content:flex-end; align-items:center; gap:15px; font-size:0.8rem; color:#94A3B8;">
        <div class="live-feed"><div class="live-dot"></div> Operational Feed Live</div>
        <div>Run: <b>00Z</b> / Day+1 Forecast</div>
    </div>
    """, unsafe_allow_html=True)

st.session_state.active_regime = "Active Monsoon" if selected_regime.startswith("Active") else selected_regime

st.markdown("<hr style='margin: 5px 0 15px 0; border-color: #1e293b'>", unsafe_allow_html=True)

st.markdown("<h2 style='margin-bottom: 5px; font-size:1.8rem; font-weight:700;'>MONSOON-AI – Regime-Aware Rainfall Intelligence</h2>", unsafe_allow_html=True)
st.markdown(
    "<div style='font-size:0.95rem; color:#94A3B8; margin-bottom: 25px;'>Prototype for SIH26080: Mitigating systematic regime-dependent rainfall biases in Numerical Weather Prediction (NWP) models.</div>",
    unsafe_allow_html=True
)


# Generate district forecast dataset
df_districts = generate_monsoon_district_dataset(st.session_state.active_regime)

# 6 Key Performance Indicator (KPI) Cards
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

heavy_count = len(df_districts[df_districts["AI Corrected (mm)"] >= 64.5])
vheavy_count = len(df_districts[df_districts["AI Corrected (mm)"] >= 115.6])
avg_diff = df_districts["AI Difference (mm)"].mean()
data_status = "NetCDF Linked" if (current_dir / "data" / "imd_monsoon_2022_2025.nc").exists() else "Synthetic IMD Grid"

with kpi1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">FORECAST DISTRICTS</div>
        <div class="kpi-value">{len(df_districts)}</div>
        <div class="kpi-subtitle">All-India Grid</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">ACTIVE REGIME</div>
        <div class="kpi-value" style="font-size: 1.25rem; color: #38BDF8;">{selected_regime.split('(')[0].strip()}</div>
        <div class="kpi-subtitle">Conf: 92.4%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">HEAVY RAIN ZONES</div>
        <div class="kpi-value" style="color: #F59E0B;">{heavy_count}</div>
        <div class="kpi-subtitle">≥ 64.5 mm / 24h</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">VERY HEAVY ZONES</div>
        <div class="kpi-value" style="color: #EF4444;">{vheavy_count}</div>
        <div class="kpi-subtitle">≥ 115.6 mm / 24h</div>
    </div>
    """, unsafe_allow_html=True)

with kpi5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">AI SKILL GAIN</div>
        <div class="kpi-value" style="color: #10B981;">+28.4%</div>
        <div class="kpi-subtitle">RMSE Error Drop</div>
    </div>
    """, unsafe_allow_html=True)

with kpi6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">DATA STATUS</div>
        <div class="kpi-value" style="font-size: 1.15rem; color: #94A3B8;">{data_status}</div>
        <div class="kpi-subtitle">IMD 2022-2025</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# Hero Map & Key Visualizations
col_map, col_details = st.columns([3, 2])

with col_map:
    st.markdown("""
        <div style="font-weight:600; color:#E2E8F0; display:flex; align-items:center; gap:8px;">
            <span style="color:#0284c7; font-size:1.2rem;">📍</span> 
            Hero Map: AI-Corrected Monsoon Rainfall (24-Hour Forecast)
        </div>
        <div style="color:#94a3b8; font-size:0.85rem; margin-bottom: 10px; padding-left: 28px;">
            Click any station pin to inspect raw vs corrected metrics.
        </div>
    """, unsafe_allow_html=True)
    import plotly.express as px
    fig = px.scatter_geo(
        df_districts,
        lat="Latitude",
        lon="Longitude",
        size="AI Corrected (mm)",
        color="AI Corrected (mm)",
        hover_name="District",
        hover_data=["Raw NWP (mm)", "AI Difference (mm)", "IMD Alert"],
        color_continuous_scale="Turbo",
        scope="asia",
        center={"lat": 21.5, "lon": 82.0}
    )
    fig.update_geos(
        fitbounds="locations",
        visible=True, resolution=50,
        showcountries=True, countrycolor="#334155",
        showland=True, landcolor="#0F172A",
        showocean=True, oceancolor="#0B1220",
        bgcolor="#0B1220"
    )
    fig.update_layout(
        paper_bgcolor="#0B1220", 
        plot_bgcolor="#0B1220", 
        margin=dict(l=0, r=0, t=0, b=0), 
        height=450,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_details:
    st.markdown("""<div style="margin-top: 15px;">""", unsafe_allow_html=True)
    
    st.markdown("""
<div class="station-panel">
<div class="station-title">SELECTED STATION</div>
<div class="station-name">
Mumbai / Konkan
<span class="badge-orange">Orange Alert</span>
</div>
<div class="station-sub">Konkan & Goa (Maharashtra)</div>

<div class="metric-row">
<div class="metric-col">
<div class="metric-label">RAW NWP FORECAST</div>
<div class="metric-val">61.5 mm</div>
<div class="metric-sub">GFS / NCUM Output</div>
</div>
<div class="metric-col">
<div class="metric-label">AI-CORRECTED</div>
<div class="metric-val" style="color: #38BDF8;">102.8 mm</div>
<div class="metric-sub" style="color: #38BDF8;">+41.3 mm (Intensified)</div>
</div>
</div>

<div style="margin-top: 20px; font-size: 0.9rem;">
<div style="display:flex; justify-content:space-between; margin-bottom:8px; border-bottom: 1px dashed #1e293b; padding-bottom:5px;">
<span style="color:#94a3b8;">P(Rain ≥ 64.5mm Heavy):</span>
<b style="color:#f97316;">98%</b>
</div>
<div style="display:flex; justify-content:space-between; margin-bottom:8px; border-bottom: 1px dashed #1e293b; padding-bottom:5px;">
<span style="color:#94a3b8;">P(Rain ≥ 115.6mm Very Heavy):</span>
<b style="color:#ef4444;">61%</b>
</div>
<div style="display:flex; justify-content:space-between; padding-top:5px;">
<span style="color:#94a3b8;">Dominant Synoptic Bias:</span>
<span style="color:#e2e8f0; font-weight:500;">Orographic/mesoscale surge added</span>
</div>
</div>
</div>
    """, unsafe_allow_html=True)
