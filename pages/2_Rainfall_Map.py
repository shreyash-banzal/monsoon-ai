"""
Page 2: Rainfall Intelligence Map
MONSOON-AI: Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from utils.map_utils import (
    generate_monsoon_district_dataset,
    create_rainfall_folium_map,
    get_color_for_rainfall
)

st.set_page_config(page_title="Rainfall Intelligence Map | MONSOON-AI", page_icon="🗺️", layout="wide")

from utils.ui import apply_custom_theme, render_sidebar
apply_custom_theme()
render_sidebar()

st.markdown("""
<style>
    .stApp { background-color: #0B1220; color: #F1F5F9; }
</style>
""", unsafe_allow_html=True)

st.title("🗺️ Rainfall Intelligence Map")
st.markdown("Multi-Layer Interactive Meteorological Explorer: Raw NWP vs AI Post-Processed Fields.")

col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 2])

with col_ctrl1:
    layer_mode = st.radio(
        "Select Map Layer",
        options=["AI Corrected", "Raw NWP", "Difference", "Heavy Rain Probability"],
        horizontal=True,
        index=0,
        help="Switch spatial field view."
    )

with col_ctrl2:
    selected_regime = st.selectbox(
        "Underlying Regime Scenario",
        options=[
            "Active Monsoon",
            "Break Monsoon",
            "Monsoon Depression / LPS",
            "Offshore Trough / Convective Surge",
            "Normal / Transition"
        ],
        index=0
    )

with col_ctrl3:
    df_all = generate_monsoon_district_dataset(selected_regime)
    states = ["All States"] + sorted(list(df_all["State"].unique()))
    state_filter = st.selectbox("Filter by State", options=states, index=0)

if state_filter != "All States":
    df_display = df_all[df_all["State"] == state_filter]
else:
    df_display = df_all

# Layer Explanation Banner
if layer_mode == "AI Corrected":
    st.info("Showing **MONSOON-AI Corrected Rainfall (mm)**: Machine learning models calibrated with regime-conditioned bias structures.")
elif layer_mode == "Raw NWP":
    st.warning("Showing **Raw Numerical Weather Prediction (GFS / NCUM) Forecast (mm)**: Direct uncorrected model grid output containing known synoptic biases.")
elif layer_mode == "Difference":
    st.success("Showing **Correction Delta (AI - Raw NWP)**: Blue represents rainfall intensified by AI; Red represents false alarm wet-bias removed by AI.")
else:
    st.error("Showing **Calibrated Probability of Heavy Rainfall (≥ 64.5 mm)**: High-resolution probabilistic risk output.")

# Folium Map
col_map, col_details = st.columns([3, 2])

with col_map:
    import plotly.express as px
    # Map 'layer_mode' names to the dataframe columns
    col_map_dict = {
        "AI Corrected": "AI Corrected (mm)",
        "Raw NWP": "Raw NWP (mm)",
        "Difference": "AI Difference (mm)",
        "Heavy Rain Probability": "Heavy Rain Prob (>=64.5mm)"
    }
    data_col = col_map_dict.get(layer_mode, "AI Corrected (mm)")

    fig = px.scatter_geo(
        df_display, lat="Latitude", lon="Longitude",
        color=data_col, size=data_col if layer_mode != "Difference" else df_display[data_col].abs(),
        hover_name="District", scope="asia",
        color_continuous_scale="Turbo"
    )
    fig.update_geos(
        fitbounds="locations", visible=True, resolution=50,
        showcountries=True, countrycolor="#334155",
        showland=True, landcolor="#0F172A", showocean=True, oceancolor="#0B1220", bgcolor="#0B1220"
    )
    fig.update_layout(paper_bgcolor="#0B1220", plot_bgcolor="#0B1220", margin=dict(l=0, r=0, t=0, b=0), height=520)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_details:
    st.subheader("📍 Station Inspector")
    station_names = list(df_display["District"].unique())
    selected_station = st.selectbox("Select Station to Inspect", options=station_names, index=0)
    station_data = df_display[df_display["District"] == selected_station].iloc[0]

    st.markdown(f"""
    #### {station_data['District']}, {station_data['State']}
    *Meteorological Subdivision:* **{station_data['Subdivision']}**
    
    | Metric | Forecast Value |
    | :--- | :--- |
    | **Raw NWP Forecast** | `{station_data['Raw NWP (mm)']} mm` |
    | **MONSOON-AI Corrected** | **`{station_data['AI Corrected (mm)']} mm`** |
    | **Post-Processing Delta** | `{station_data['AI Difference (mm)']:+} mm` |
    | **P(Rain ≥ 64.5 mm)** | `{station_data['Heavy Rain Prob (>=64.5mm)'] * 100:.1f}%` |
    | **P(Rain ≥ 115.6 mm)** | `{station_data['Very Heavy Prob (>=115.6mm)'] * 100:.1f}%` |
    | **IMD Operational Alert** | `{station_data['IMD Alert']}` |
    """)

    if station_data['AI Difference (mm)'] > 5:
        st.write("🟢 **AI Diagnosis**: Underprediction detected in raw model. AI applied positive orographic/convective reinforcement.")
    elif station_data['AI Difference (mm)'] < -5:
        st.write("🔴 **AI Diagnosis**: Spurious wet bias detected in raw model. AI suppressed false rainfall signal.")
    else:
        st.write("⚪ **AI Diagnosis**: Raw model aligned reasonably well with synoptic thermodynamics.")

# Full Data Table
st.markdown("### 📋 Complete Spatial Station Data")
st.dataframe(df_display, hide_index=True, use_container_width=True)
