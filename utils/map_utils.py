"""
MONSOON-AI Map & Visualization Utilities
Generates Folium interactive choropleth/marker maps and Plotly meteorological visualizers.
"""

from typing import Dict, Any, List, Optional
import folium
from folium.plugins import HeatMap
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Key Meteorological Subdivisions & High-Impact Monsoon Districts in India
KEY_MONSOON_LOCATIONS = [
    {"name": "Mumbai / Konkan", "state": "Maharashtra", "lat": 19.0760, "lon": 72.8777, "subdiv": "Konkan & Goa", "typical_bias": "underestimate"},
    {"name": "Ratnagiri", "state": "Maharashtra", "lat": 16.9902, "lon": 73.3120, "subdiv": "Konkan & Goa", "typical_bias": "underestimate"},
    {"name": "Mahabaleshwar", "state": "Maharashtra", "lat": 17.9237, "lon": 73.6586, "subdiv": "Madhya Maharashtra", "typical_bias": "underestimate"},
    {"name": "Pune", "state": "Maharashtra", "lat": 18.5204, "lon": 73.8567, "subdiv": "Madhya Maharashtra", "typical_bias": "neutral"},
    {"name": "Nagpur / Vidarbha", "state": "Maharashtra", "lat": 21.1458, "lon": 79.0882, "subdiv": "Vidarbha", "typical_bias": "overestimate_break"},
    {"name": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lon": 77.4126, "subdiv": "West MP", "typical_bias": "overestimate_break"},
    {"name": "Jabalpur", "state": "Madhya Pradesh", "lat": 23.1815, "lon": 79.9864, "subdiv": "East MP", "typical_bias": "underestimate_lps"},
    {"name": "Raipur", "state": "Chhattisgarh", "lat": 21.2514, "lon": 81.6296, "subdiv": "Chhattisgarh", "typical_bias": "underestimate_lps"},
    {"name": "Bhubaneswar", "state": "Odisha", "lat": 20.2961, "lon": 85.8245, "subdiv": "Odisha", "typical_bias": "underestimate_lps"},
    {"name": "Puri", "state": "Odisha", "lat": 19.8135, "lon": 85.8312, "subdiv": "Odisha", "typical_bias": "underestimate_lps"},
    {"name": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lon": 88.3639, "subdiv": "Gangetic West Bengal", "typical_bias": "underestimate_lps"},
    {"name": "Guwahati", "state": "Assam", "lat": 26.1445, "lon": 91.7362, "subdiv": "Assam & Meghalaya", "typical_bias": "underestimate_break"},
    {"name": "Cherrapunji (Sohra)", "state": "Meghalaya", "lat": 25.2702, "lon": 91.7323, "subdiv": "Assam & Meghalaya", "typical_bias": "underestimate"},
    {"name": "Patna", "state": "Bihar", "lat": 25.5941, "lon": 85.1376, "subdiv": "Bihar", "typical_bias": "overestimate"},
    {"name": "Varanasi", "state": "Uttar Pradesh", "lat": 25.3176, "lon": 82.9739, "subdiv": "East UP", "typical_bias": "overestimate"},
    {"name": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lon": 80.9462, "subdiv": "East UP", "typical_bias": "overestimate"},
    {"name": "New Delhi", "state": "Delhi", "lat": 28.6139, "lon": 77.2090, "subdiv": "Haryana & Delhi", "typical_bias": "overestimate_break"},
    {"name": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lon": 75.7873, "subdiv": "East Rajasthan", "typical_bias": "overestimate"},
    {"name": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lon": 72.5714, "subdiv": "Gujarat Region", "typical_bias": "underestimate_lps"},
    {"name": "Surat", "state": "Gujarat", "lat": 21.1702, "lon": 72.8311, "subdiv": "Gujarat Region", "typical_bias": "underestimate"},
    {"name": "Kochi", "state": "Kerala", "lat": 9.9312, "lon": 76.2673, "subdiv": "Kerala & Mahe", "typical_bias": "underestimate"},
    {"name": "Wayanad", "state": "Kerala", "lat": 11.6854, "lon": 76.1320, "subdiv": "Kerala & Mahe", "typical_bias": "underestimate"},
    {"name": "Mangaluru", "state": "Karnataka", "lat": 12.9141, "lon": 74.8560, "subdiv": "Coastal Karnataka", "typical_bias": "underestimate"},
    {"name": "Bengaluru", "state": "Karnataka", "lat": 12.9716, "lon": 77.5946, "subdiv": "South Interior Karnataka", "typical_bias": "neutral"},
    {"name": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lon": 78.4867, "subdiv": "Telangana", "typical_bias": "underestimate_lps"},
    {"name": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.6868, "lon": 83.2185, "subdiv": "Coastal AP", "typical_bias": "underestimate_lps"},
    {"name": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lon": 80.2707, "subdiv": "Tamil Nadu", "typical_bias": "neutral"}
]


def generate_monsoon_district_dataset(regime_name: str = "Active Monsoon") -> pd.DataFrame:
    """
    Creates a calibrated district-level dataset with Raw NWP and AI-Corrected values
    reflecting real physical biases for the specified regime.
    """
    records = []
    np.random.seed(101)

    for loc in KEY_MONSOON_LOCATIONS:
        # Base realistic rainfall distribution
        if "Konkan" in loc["subdiv"] or "Kerala" in loc["subdiv"] or "Coastal Karnataka" in loc["subdiv"]:
            base_rain = np.random.uniform(55.0, 140.0)
        elif "Meghalaya" in loc["subdiv"] or "Assam" in loc["subdiv"]:
            base_rain = np.random.uniform(40.0, 130.0)
        elif "MP" in loc["subdiv"] or "Chhattisgarh" in loc["subdiv"] or "Odisha" in loc["subdiv"]:
            base_rain = np.random.uniform(30.0, 95.0)
        else:
            base_rain = np.random.uniform(5.0, 45.0)

        # Apply regime specific physical bias signatures
        if regime_name == "Break Monsoon":
            if loc["subdiv"] in ["Assam & Meghalaya", "Sub-Himalayan West Bengal"]:
                raw_nwp = base_rain * 0.75
                ai_corrected = base_rain * 1.30 + 15.0
            else:
                raw_nwp = base_rain * 1.85 + 18.0
                ai_corrected = max(0.5, base_rain * 0.35)
        elif regime_name == "Monsoon Depression / LPS":
            if loc["subdiv"] in ["Odisha", "Gangetic West Bengal", "Chhattisgarh", "Vidarbha", "East MP"]:
                raw_nwp = base_rain * 0.70
                ai_corrected = base_rain * 1.45 + 25.0
            else:
                raw_nwp = base_rain * 1.10
                ai_corrected = base_rain * 0.95
        elif regime_name == "Offshore Trough / Convective Surge":
            if "Konkan" in loc["subdiv"] or "Coastal Karnataka" in loc["subdiv"] or "Kerala" in loc["subdiv"]:
                raw_nwp = base_rain * 0.65
                ai_corrected = base_rain * 1.50 + 30.0
            else:
                raw_nwp = base_rain * 1.05
                ai_corrected = base_rain * 0.90
        else:  # Active Monsoon
            if "Konkan" in loc["subdiv"] or "Madhya Maharashtra" in loc["subdiv"] or "MP" in loc["subdiv"]:
                raw_nwp = base_rain * 0.82
                ai_corrected = base_rain * 1.25 + 10.0
            else:
                raw_nwp = base_rain * 1.15
                ai_corrected = base_rain * 0.92

        raw_nwp = round(float(raw_nwp), 1)
        ai_corrected = round(float(ai_corrected), 1)
        diff = round(ai_corrected - raw_nwp, 1)

        # Probabilities
        prob_64_5 = round(float(1.0 / (1.0 + np.exp(-(ai_corrected - 55.0) / 12.0))), 3)
        prob_115_6 = round(float(1.0 / (1.0 + np.exp(-(ai_corrected - 95.0) / 18.0))), 3)
        prob_204_5 = round(float(1.0 / (1.0 + np.exp(-(ai_corrected - 170.0) / 25.0))), 3)

        # Alert level
        if prob_204_5 >= 0.40 or ai_corrected >= 160:
            alert = "Red"
        elif prob_115_6 >= 0.50 or ai_corrected >= 95:
            alert = "Orange"
        elif prob_64_5 >= 0.45 or ai_corrected >= 55:
            alert = "Yellow"
        else:
            alert = "Green"

        records.append({
            "District": loc["name"],
            "State": loc["state"],
            "Subdivision": loc["subdiv"],
            "Latitude": loc["lat"],
            "Longitude": loc["lon"],
            "Raw NWP (mm)": raw_nwp,
            "AI Corrected (mm)": ai_corrected,
            "AI Difference (mm)": diff,
            "Heavy Rain Prob (>=64.5mm)": prob_64_5,
            "Very Heavy Prob (>=115.6mm)": prob_115_6,
            "Extremely Heavy Prob (>=204.5mm)": prob_204_5,
            "IMD Alert": alert
        })

    return pd.DataFrame(records)


def get_color_for_rainfall(val: float) -> str:
    """Returns meteorological standard color code for 24h rainfall (mm)."""
    if val >= 204.5:
        return "#7F1D1D"  # Extremely heavy (Deep Crimson)
    elif val >= 115.6:
        return "#DC2626"  # Very heavy (Red)
    elif val >= 64.5:
        return "#EA580C"  # Heavy (Orange)
    elif val >= 35.5:
        return "#EAB308"  # Moderate (Yellow)
    elif val >= 7.5:
        return "#10B981"  # Light-Moderate (Emerald)
    elif val >= 2.5:
        return "#06B6D4"  # Light (Cyan)
    else:
        return "#64748B"  # Very light / Dry (Slate)


def get_color_for_diff(val: float) -> str:
    """Divergent color for difference (Positive = Green/Blue, Negative = Amber/Red)."""
    if val > 15:
        return "#2563EB"  # Substantial upward correction
    elif val > 0:
        return "#0284C7"
    elif val < -15:
        return "#DC2626"  # Substantial wet bias removal
    else:
        return "#D97706"


def create_rainfall_folium_map(
    df: pd.DataFrame,
    layer_type: str = "AI Corrected",
    center: List[float] = [21.5, 80.0],
    zoom: int = 5
) -> folium.Map:
    """
    Creates an interactive dark-themed Folium map with meteorological styling.
    Supports layers: 'AI Corrected', 'Raw NWP', 'Difference', 'Heavy Rain Probability'.
    """
    # High-contrast CartoDB dark tiles
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="CartoDB dark_matter",
        control_scale=True
    )

    for _, row in df.iterrows():
        lat = row["Latitude"]
        lon = row["Longitude"]
        dist = row["District"]
        state = row["State"]
        nwp = row["Raw NWP (mm)"]
        ai = row["AI Corrected (mm)"]
        diff = row["AI Difference (mm)"]
        prob = row["Heavy Rain Prob (>=64.5mm)"]
        alert = row["IMD Alert"]

        if layer_type == "AI Corrected":
            val = ai
            color = get_color_for_rainfall(val)
            radius = max(6, min(24, int(val / 6)))
            label = f"AI Corrected: {val} mm"
        elif layer_type == "Raw NWP":
            val = nwp
            color = get_color_for_rainfall(val)
            radius = max(6, min(24, int(val / 6)))
            label = f"Raw NWP: {val} mm"
        elif layer_type == "Difference":
            val = diff
            color = get_color_for_diff(val)
            radius = max(6, min(24, int(abs(val) / 3)))
            label = f"AI - NWP Delta: {val:+} mm"
        else:  # Heavy Rain Probability
            val = prob * 100
            color = "#DC2626" if val >= 65 else ("#F97316" if val >= 45 else ("#EAB308" if val >= 25 else "#10B981"))
            radius = max(6, min(24, int(val / 4.5)))
            label = f"P(Rain >= 64.5mm): {val:.1f}%"

        popup_html = f"""
        <div style="font-family: sans-serif; min-width: 180px; background: #0F172A; color: #F8FAFC; padding: 10px; border-radius: 8px; border: 1px solid #334155;">
            <h4 style="margin: 0 0 6px 0; color: #38BDF8; font-size: 14px;">{dist}, {state}</h4>
            <div style="font-size: 12px; line-height: 1.5;">
                <b>Raw NWP:</b> {nwp} mm<br/>
                <b>AI Corrected:</b> <span style="color: #4ADE80; font-weight: bold;">{ai} mm</span><br/>
                <b>Adjustment:</b> <span style="color: {'#60A5FA' if diff > 0 else '#F87171'};">{diff:+} mm</span><br/>
                <b>Heavy Rain Prob:</b> {prob * 100:.1f}%<br/>
                <b>IMD Alert Status:</b> <span style="font-weight: bold; color: {color};">{alert}</span>
            </div>
        </div>
        """

        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color=color,
            weight=2,
            fill=True,
            fill_color=color,
            fill_opacity=0.75,
            tooltip=f"{dist}: {label} ({alert} Alert)",
            popup=folium.Popup(popup_html, max_width=250)
        ).add_to(m)

    return m


def create_plotly_comparison_chart(df: pd.DataFrame, top_n: int = 12) -> go.Figure:
    """Creates side-by-side bar chart of Raw NWP vs AI-Corrected rainfall."""
    sample = df.sort_values(by="AI Corrected (mm)", ascending=False).head(top_n)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sample["District"],
        y=sample["Raw NWP (mm)"],
        name="Raw NWP (GFS/NCUM)",
        marker_color="#94A3B8"
    ))
    fig.add_trace(go.Bar(
        x=sample["District"],
        y=sample["AI Corrected (mm)"],
        name="MONSOON-AI Corrected",
        marker_color="#38BDF8"
    ))

    fig.update_layout(
        title="High-Impact Districts: Raw NWP vs MONSOON-AI Corrected Forecast",
        barmode="group",
        paper_bgcolor="#0B1220",
        plot_bgcolor="#111827",
        font=dict(color="#E2E8F0"),
        xaxis=dict(gridcolor="#1E293B", tickangle=-35),
        yaxis=dict(gridcolor="#1E293B", title="24h Rainfall (mm)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=80)
    )
    return fig
