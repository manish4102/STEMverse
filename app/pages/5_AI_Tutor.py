# pages/5_AI_Tutor.py

import os
import streamlit as st
from utils import tutor, a11y  # keeps your keyword fallback + TTS

MODEL_NAME = "gemini-1.5-flash"

def _try_gemini(prompt: str) -> str:
    """Return Gemini answer using backend env only. Raise to let caller fallback."""
    key = os.getenv("GEMINI_API_KEY", "AIzaSyAyPgJs77nhdr8HxRp1IzQIcPXt2hLxyVM")
    if not key:
        raise RuntimeError("Gemini not configured")
    try:
        import google.generativeai as genai
    except Exception as e:
        raise RuntimeError("google-generativeai not installed") from e

    genai.configure(api_key=key)
    model = genai.GenerativeModel(MODEL_NAME)
    resp = model.generate_content(prompt)

    # Safely extract text
    text = ""
    try:
        text = (resp.text or "").strip()
    except Exception:
        try:
            text = "\n".join(
                p.text for p in resp.candidates[0].content.parts if getattr(p, "text", None)
            ).strip()
        except Exception:
            text = ""

    if not text:
        raise RuntimeError("Empty Gemini response")
    return text

st.title("🤖 AI Tutor")

prompt = st.text_area(
    "Ask a STEM question",
    placeholder="e.g., Explain torque with a bike example",
    height=120,
)

col_a, col_b = st.columns(2)
with col_a:
    ask = st.button("Ask")
with col_b:
    clear = st.button("Clear")

if clear:
    st.session_state.pop("ai_tutor_last", None)
    st.rerun()

if ask and prompt.strip():
    try:
        # Try Gemini (backend only; no UI key)
        answer = _try_gemini(prompt)
        st.session_state["ai_tutor_last"] = answer
    except Exception:
        # Silent, safe fallback to keyword tutor
        ans, vid = tutor.lookup_response(prompt)
        out = ans + (f"\n\nSuggested video: {vid}" if vid else "")
        st.session_state["ai_tutor_last"] = out

# Render answer (both Gemini and fallback)
if "ai_tutor_last" in st.session_state:
    st.subheader("Answer")
    st.write(st.session_state["ai_tutor_last"])
    a11y.tts_button(st.session_state["ai_tutor_last"], key="tts_ai_answer")
