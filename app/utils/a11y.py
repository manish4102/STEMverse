# utils/a11y.py
# Browser-first TTS: uses Web Speech API via a small Streamlit component.
# Works on Python 3.9+. Keeps the same call: a11y.tts_button("text", key=..., lang="en-US", rate=1.0)

import hashlib
import json
import streamlit as st
import streamlit.components.v1 as components
from typing import Optional

def _make_key(text: str, key: Optional[str]) -> str:
    if key:
        return key
    return "tts_" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]

def tts_button(
    text: str,
    key: Optional[str] = None,
    label: str = "🔊 Read aloud",
    *,
    lang: Optional[str] = None,   # e.g. "en-US", "en-GB", "hi-IN"
    rate: Optional[float] = None, # 0.1 .. 10.0 (1.0 normal)
    pitch: Optional[float] = None # 0 .. 2 (1.0 normal)
):
    """
    Renders an in-browser TTS control using the Web Speech API.
    If the browser doesn't support it, we show a friendly message.
    """
    if not text or not text.strip():
        return

    cfg = {
        "text": text.strip(),
        "lang": lang or st.session_state.get("a11y_lang", "en-US"),
        "rate": float(rate) if rate is not None else 1.0,
        "pitch": float(pitch) if pitch is not None else 1.0,
        "label": label,
    }
    cid = _make_key(cfg["text"], key)

    # Note: JSON-encode to safely pass content into JS (handles quotes/newlines)
    payload = json.dumps(cfg)

    html = f"""
<div id="wrap-{cid}" style="display:flex;align-items:center;gap:.5rem;">
  <button id="play-{cid}" aria-label="{cfg['label']}" style="min-height:48px;">{cfg['label']}</button>
  <button id="stop-{cid}" aria-label="Stop" style="min-height:48px;">⏹ Stop</button>
  <span id="status-{cid}" aria-live="polite" style="margin-left:.25rem;"></span>
</div>
<script>
(function() {{
  const cfg = {payload};
  const synth = window.speechSynthesis;
  const playBtn = document.getElementById("play-{cid}");
  const stopBtn = document.getElementById("stop-{cid}");
  const status  = document.getElementById("status-{cid}");

  if (!synth) {{
    status.textContent = "Browser TTS not supported here.";
    return;
  }}

  let utter = null;

  function speak() {{
    try {{
      if (utter) synth.cancel();
      utter = new SpeechSynthesisUtterance(cfg.text);
      utter.lang  = cfg.lang || "en-US";
      utter.rate  = cfg.rate || 1.0;
      utter.pitch = cfg.pitch || 1.0;

      // Prefer a matching voice if available
      const voices = synth.getVoices();
      if (voices && voices.length) {{
        const match = voices.find(v => (v.lang||"").toLowerCase() === utter.lang.toLowerCase());
        if (match) utter.voice = match;
      }}

      utter.onstart = () => {{ status.textContent = "Playing…"; }};
      utter.onend   = () => {{ status.textContent = "Done"; }};
      utter.onerror = () => {{ status.textContent = "Speech error"; }};
      synth.speak(utter);
    }} catch (e) {{
      status.textContent = "Speech failed";
      console.error(e);
    }}
  }}

  playBtn.addEventListener("click", speak);
  stopBtn.addEventListener("click", () => {{
    try {{ synth.cancel(); status.textContent = "Stopped"; }} catch (e) {{}}
  }});

  // Some browsers (Chrome) load voices asynchronously — refresh voice list once.
  if (typeof speechSynthesis !== "undefined" && speechSynthesis.onvoiceschanged !== undefined) {{
    speechSynthesis.onvoiceschanged = function () {{}};
  }}
}})();
</script>
"""
    # Height small because we render our own buttons; no audio player bar
    components.html(html, height=60)

# --- Accessibility CSS injector (works with Home.py: a11y.inject_global_styles(hc, lt)) ---
import streamlit as st

def inject_global_styles(high_contrast=False, large_text=False, reduced_motion=False):
    """
    Inject global CSS for accessibility:
      - high_contrast: stronger colors + visible focus
      - large_text: ~18px base, larger headings
      - reduced_motion: disables CSS animations/transitions
      - always enforces 48px+ touch targets
    Usage (as in Home.py):
        a11y.inject_global_styles(hc, lt)
    """
    base_css = """
    <style>
      /* Minimum touch target size */
      button, .stButton>button, .stDownloadButton>button,
      [data-testid="stSidebarNav"] a, .stSlider, .stSelectbox, .stTextInput,
      .stTextArea, .stToggle, .stRadio, .stCheckbox {
        min-height: 48px;
      }
      /* Clear, visible focus ring */
      *:focus { outline: 3px solid #ffd400 !important; outline-offset: 2px !important; }
    """
    hc_css = """
      /* High contrast mode */
      [data-testid="stAppViewContainer"] { background: #0d0d0d !important; color: #ffffff !important; }
      .stMarkdown, .stCaption, .stText, .stAlert, .stRadio, .stCheckbox, .stSlider { color: #ffffff !important; }
      .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background: #111 !important; color: #fff !important; border: 2px solid #bbb !important; border-radius: 10px;
      }
      .stButton>button, .stDownloadButton>button {
        background: #000 !important; color: #fff !important; border: 2px solid #fff !important; border-radius: 12px;
      }
      a { color: #4da3ff !important; text-decoration: underline; }
    """
    lt_css = """
      /* Large text mode */
      html, body { font-size: 18px !important; line-height: 1.6 !important; }
      h1 { font-size: 2.0rem !important; }  h2 { font-size: 1.6rem !important; }  h3 { font-size: 1.3rem !important; }
    """
    rm_css = """
      /* Reduced motion */
      * { animation: none !important; transition: none !important; scroll-behavior: auto !important; }
    """
    end_css = "</style>"

    parts = [base_css]
    if high_contrast: parts.append(hc_css)
    if large_text:    parts.append(lt_css)
    if reduced_motion:parts.append(rm_css)
    parts.append(end_css)

    st.markdown("\n".join(parts), unsafe_allow_html=True)
