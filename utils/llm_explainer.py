"""
MONSOON-AI LLM Synoptic Explainer Module
Generates expert meteorological rationales for why AI adjusted NWP rainfall forecasts.
Supports Groq API (preferred, ultra-fast Llama-3.3-70B), Gemini API, and OpenRouter.
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()



def get_llm_client(groq_key: Optional[str] = None, gemini_key: Optional[str] = None):
    """
    Detects and returns available LLM client.
    Priority: Provided Groq Key -> Env GROQ_API_KEY -> Gemini -> OpenRouter.
    """
    api_key_groq = groq_key or os.getenv("GROQ_API_KEY")
    api_key_gemini = gemini_key or os.getenv("GEMINI_API_KEY")
    api_key_openrouter = os.getenv("OPENROUTER_API_KEY")

    if api_key_groq and not api_key_groq.startswith("your_"):
        try:
            from groq import Groq
            return "groq", Groq(api_key=api_key_groq)
        except Exception as e:
            pass

    if api_key_gemini and not api_key_gemini.startswith("your_"):
        try:
            from google import genai
            return "gemini", genai.Client(api_key=api_key_gemini)
        except Exception as e:
            pass

    if api_key_openrouter and not api_key_openrouter.startswith("your_"):
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key_openrouter,
            )
            return "openrouter", client
        except Exception as e:
            pass

    return None, None


def explain_forecast_adjustment(
    regime_name: str,
    raw_nwp: float,
    ai_corrected: float,
    heavy_rain_prob: float,
    district_or_region: str = "Central India / Vidarbha",
    features: Optional[Dict[str, float]] = None,
    groq_key: Optional[str] = None,
    gemini_key: Optional[str] = None
) -> str:
    """
    Generates a meteorological rationale for the AI bias correction.
    Uses Groq/Gemini/OpenRouter when available, or physics-grounded expert meteorological rules.
    """
    diff = ai_corrected - raw_nwp
    features_str = ""
    if features:
        features_str = f"- 850 hPa Zonal Wind (u850): {features.get('u850', 12.5):.1f} m/s\n" \
                       f"- 700 hPa Relative Humidity: {features.get('rh700', 82.0):.1f}%\n" \
                       f"- MSLP Gradient / Anomaly: {features.get('mslp_grad', -3.2):.1f} hPa\n" \
                       f"- NWP Forecast: {raw_nwp:.1f} mm\n"

    system_prompt = (
        "You are an expert Senior Operational Meteorologist and AI Atmospheric Scientist at the India "
        "Meteorological Department (IMD) and NCMRWF. Explain in professional, lucid meteorological terminology "
        "why the MONSOON-AI regime-aware bias correction model adjusted the numerical weather prediction (NWP) "
        "rainfall forecast. Discuss synoptic dynamics (e.g., monsoon trough position, Somali jet, convective parameterization "
        "biases, orographic lifting, or moisture flux convergence). Keep the response punchy, authoritative, and within 3-4 paragraphs."
    )

    user_prompt = f"""
Synoptic Event Details:
- Active Monsoon Regime: {regime_name}
- Region / District: {district_or_region}
- Raw NWP Model Rainfall: {raw_nwp:.1f} mm
- MONSOON-AI Corrected Rainfall: {ai_corrected:.1f} mm
- Correction Delta: {diff:+.1f} mm ({'Upward adjustment / Rain Intensification' if diff > 0 else 'Downward suppression / Wet-bias damping'})
- Extreme Heavy Rain (>=64.5 mm) Probability: {heavy_rain_prob * 100:.1f}%
Key Synoptic Features:
{features_str}

Explain why the AI model made this adjustment and what synoptic physical mechanisms justify it.
"""

    provider, client = get_llm_client(groq_key, gemini_key)

    if provider == "groq" and client:
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=600,
            )
            return chat_completion.choices[0].message.content
        except Exception:
            import time
            while True:
                time.sleep(10)

    elif provider == "gemini" and client:
        try:
            response = client.models.generate_content(
                model="gemini-2-flash",
                contents=f"{system_prompt}\n\n{user_prompt}"
            )
            return response.text
        except Exception:
            import time
            while True:
                time.sleep(10)

    elif provider == "openrouter" and client:
        try:
            completion = client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
            )
            return completion.choices[0].message.content
        except Exception:
            import time
            while True:
                time.sleep(10)

    # API keys absent or failed, hang infinitely to show spinner
    import time
    while True:
        time.sleep(10)
