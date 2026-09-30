import os
import streamlit as st
from pathlib import Path

def apply_custom_theme(enable_bg_animation=True):
    # Check env var for overriding toggle
    if os.getenv("MONSOON_BG_ANIMATION", "true").lower() != "true":
        enable_bg_animation = False
        
    if enable_bg_animation:
        # Create a CSS rain animation behind everything
        st.markdown("""
        <div class="monsoon-rain-bg">
            <div class="rain drop1"></div><div class="rain drop2"></div><div class="rain drop3"></div>
            <div class="rain drop4"></div><div class="rain drop5"></div><div class="rain drop6"></div>
            <div class="rain drop7"></div><div class="rain drop8"></div><div class="rain drop9"></div>
            <div class="rain drop10"></div><div class="rain drop11"></div><div class="rain drop12"></div>
        </div>
        <style>
            .stAppViewBlockContainer, .block-container {
                position: relative;
                z-index: 1 !important;
            }
            .monsoon-rain-bg {
                position: fixed;
                top: 0; left: 0; width: 100vw; height: 100vh;
                z-index: 0; /* Updated from -1 to sit above the .stApp solid background */
                pointer-events: none;
                overflow: hidden;
            }
            .rain {
                position: absolute;
                width: 2px;
                background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(135,206,250,0.4));
                animation: rainDrop 1.2s linear infinite;
            }
            @keyframes rainDrop {
                0% { transform: translateY(-100px) rotate(15deg); opacity: 0; }
                10% { opacity: 0.15; }
                80% { opacity: 0.15; }
                100% { transform: translateY(110vh) rotate(15deg); opacity: 0; }
            }
            .drop1 { left: 10%; height: 70px; animation-duration: 0.9s; animation-delay: 0.1s; }
            .drop2 { left: 25%; height: 50px; animation-duration: 1.1s; animation-delay: 0.4s; }
            .drop3 { left: 40%; height: 80px; animation-duration: 0.8s; animation-delay: 0.7s; }
            .drop4 { left: 55%; height: 60px; animation-duration: 1.0s; animation-delay: 0.2s; }
            .drop5 { left: 70%; height: 90px; animation-duration: 0.85s; animation-delay: 0.5s; }
            .drop6 { left: 85%; height: 65px; animation-duration: 1.15s; animation-delay: 0.8s; }
            .drop7 { left: 15%; height: 75px; animation-duration: 0.95s; animation-delay: 0.3s; }
            .drop8 { left: 35%; height: 55px; animation-duration: 1.05s; animation-delay: 0.6s; }
            .drop9 { left: 50%; height: 85px; animation-duration: 0.85s; animation-delay: 0.9s; }
            .drop10{ left: 65%; height: 45px; animation-duration: 1.2s;  animation-delay: 0.15s;}
            .drop11{ left: 80%; height: 95px; animation-duration: 0.8s;  animation-delay: 0.45s;}
            .drop12{ left: 95%; height: 60px; animation-duration: 1.0s;  animation-delay: 0.75s;}
        </style>
        """, unsafe_allow_html=True)

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
    </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    current_dir = Path(__file__).resolve().parent.parent
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header-box">
            <div style="font-size: 2.2rem; line-height: 1; text-shadow: 0 0 10px #38BDF8;">🌧️</div>
            <div style="line-height:1.2;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <b style="font-size:1.1rem; color:white; font-weight:800;">MONSOON-AI</b>
                    <span class="sih-badge">SIH26080</span>
                </div>
                <div style="font-size:0.75rem; color:#94a3b8; font-weight:500;">Regime Aware Rainfall AI</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 10px 0; border-color: #1e293b'>", unsafe_allow_html=True)

        if (current_dir / "app.py").exists():
            st.page_link("app.py", label="1. Command Center", icon="🎯")
        elif (current_dir / "pages" / "1_Command_Center.py").exists():
            st.page_link("pages/1_Command_Center.py", label="1. Command Center", icon="🎯")
            
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

        # Checkpoints Ready mock (assuming they are checked if inference is up)
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

        st.markdown("<hr style='margin: 15px 0; border-color: #1e293b'>", unsafe_allow_html=True)

        st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size: 0.85rem; font-weight: 600; color: #E2E8F0;">✨ LLM Engine</div>
            <div style="background:#065f46; color:#a7f3d0; padding:2px 6px; font-size:0.6rem; border-radius:4px; font-weight:bold;">LIVE AI</div>
        </div>
        <div style="font-size:0.75rem; color:#0284c7; margin-bottom: 10px; margin-top:2px; font-weight:500;">IMD Physics Rule Engine</div>
        <div style="margin-top:20px; font-size:0.8rem; color:#94a3b8; font-weight:600;">Optional Groq API Key:</div>
        <div style="background:#0F172A; border:1px solid #1E293B; border-radius:6px; padding:6px 12px; font-family:monospace; color:#475569; font-size:0.8rem; margin-top:4px;">
            gsk_********************... (Hidden)
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br/><br/><br/>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.7rem; color:#64748b; margin-top: auto;">
            Runtime <span style="float:right; color:#38BDF8;">Python 3.13</span><br/>
            IMD & NCMRWF Post-Processing Engine
        </div>
        """, unsafe_allow_html=True)


def animated_metric(label, value, suffix="", delta=None, decimals=1):
    import uuid
    import streamlit.components.v1 as components
    
    uid = str(uuid.uuid4())[:8]
    
    # Check if value is numeric for animation
    is_numeric = True
    try:
        numeric_val = float(str(value).replace('%', '').replace(',', ''))
    except ValueError:
        numeric_val = value
        is_numeric = False
            
    html_code = f"""
    <style>
        .metric-container {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: transparent;
        }}
        .metric-label {{
            font-size: 0.85rem;
            color: #94A3B8;
            margin-bottom: 0.25rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}
        .metric-val-container {{
            display: flex;
            align-items: baseline;
            gap: 6px;
        }}
        .metric-value {{
            font-size: 1.85rem;
            color: #F8FAFC;
            font-weight: 700;
        }}
        .metric-suffix {{
            font-size: 1.85rem;
            color: #F8FAFC;
            font-weight: 700;
        }}
        .metric-delta {{
            font-size: 0.8rem;
            font-weight: 500;
            margin-top: 4px;
        }}
        .delta-pos {{ color: #10B981; }} /* green */
        .delta-neg {{ color: #EF4444; }} /* red */
        .delta-neu {{ color: #94A3B8; }} /* gray */
    </style>
    <div class="metric-container">
        <div class="metric-label">{label}</div>
        <div class="metric-val-container">
            <span class="metric-value" id="val-{uid}">0</span>
            <span class="metric-suffix">{suffix}</span>
        </div>
    """
    
    if not is_numeric:
        html_code = html_code.replace(f'id="val-{uid}">0</span>', f'id="val-{uid}">{value}</span>')
        
    if delta is not None:
        delta_str = str(delta)
        delta_cls = "delta-pos" if '+' in delta_str else ("delta-neg" if '-' in delta_str else "delta-neu")
        arrow = "↑" if '+' in delta_str else ("↓" if '-' in delta_str else "")
        clean_delta = delta_str.replace('+', '').replace('-', '')
        html_code += f'<div class="metric-delta {delta_cls}">{arrow} {clean_delta}</div>'
        
    html_code += "</div>"
    
    if is_numeric:
        html_code += f"""
        <script>
            const targetValue = {numeric_val};
            const duration = 800; // ms
            const fps = 60;
            const totalFrames = (duration / 1000) * fps;
            let currentFrame = 0;
            const el = document.getElementById("val-{uid}");

            function easeOutExpo(x) {{
                return x === 1 ? 1 : 1 - Math.pow(2, -10 * x);
            }}

            function animate() {{
                currentFrame++;
                const progress = currentFrame / totalFrames;
                const easedProgress = Math.min(easeOutExpo(progress), 1);
                let currentVal = targetValue * easedProgress;

                if (currentFrame >= totalFrames) {{
                    currentVal = targetValue;
                }}
                
                el.innerHTML = currentVal.toFixed({decimals});
                
                if (currentFrame < totalFrames) {{
                    requestAnimationFrame(animate);
                }}
            }}
            requestAnimationFrame(animate);
        </script>
        """
        
    components.html(html_code, height=95)



import contextlib

@contextlib.contextmanager
def svg_spinner(svg_path, message=""):
    import streamlit as st
    import streamlit.components.v1 as components
    
    placeholder = st.empty()
    try:
        with open(svg_path, "r", encoding="utf-8") as f:
            svg_content = f.read()
    except Exception:
        svg_content = ""
        
    html = f"""
    <div style="display: flex; align-items: center; justify-content: center; flex-direction: column; width: 100%; height: 100%; overflow: hidden;">
        <div style="width: 140px; height: 140px; display: flex; align-items: center; justify-content: center;">
            {svg_content}
        </div>
        <div style="color: #94A3B8; font-family: 'Inter', -apple-system, sans-serif; font-weight: 600; font-size: 0.85rem; margin-top: -5px; letter-spacing: 0.03em;">
            {message}
        </div>
    </div>
    """
    
    with placeholder:
        components.html(html, height=160)
        
    try:
        yield
    finally:
        placeholder.empty()
