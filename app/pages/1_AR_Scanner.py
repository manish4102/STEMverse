# pages/1_AR_Scanner.py
import os, json, re
import numpy as np
import streamlit as st
import cv2
from PIL import Image
from utils import a11y, video, i18n
from utils import ar as arutil
from utils import state, layout  # <-- layout for shared sidebar
from utils.paths import DB_PATH

DB_PATH = "db/stemverse.sqlite"
st.set_page_config(page_title="AR Scanner", layout="wide")

# Language for this page (from session or DB)
uid = state.get_user_id()
LANG = i18n.init_from_session_or_db(default="en-US", db_path=DB_PATH, uid=uid)

# Sidebar (same on every page)
with st.sidebar:
    settings = layout.render_sidebar(DB_PATH, uid)
    # If user changes language here, update our local LANG too:
    LANG = settings["lang_code"]

st.title("🔎 " + i18n.t("ar.title", "AR Scanner"))
st.caption(i18n.t(
    "ar.hint",
    "Upload an image (circuit, plant, code screenshot, bicycle). AR analyzes it and explains what it sees. "
))

uploaded = st.file_uploader(i18n.t("ar.upload", "Upload image"), type=["png", "jpg", "jpeg"])
cam = st.camera_input(i18n.t("ar.capture", "Or capture from camera"))

# --- helper: robust JSON extraction from LLM text ---
def _extract_json(s: str):
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        pass
    m = re.search(r"\{.*\}", s, flags=re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None

# --- AI vision call (Gemini 1.5 Flash), backend env only ---
def ai_describe_image(pil_img: Image.Image, out_lang: str):
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        raise RuntimeError("Gemini not configured")
    try:
        import google.generativeai as genai
    except Exception as e:
        raise RuntimeError("google-generativeai not installed") from e

    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = (
        "You are a STEM visual analyst. Look at the image and decide a high-level domain.\n"
        "Possible domains: circuit, plant, code, bicycle, other.\n"
        "If it's a circuit diagram, pick 'circuit'. If it's source code/screenshot of code, pick 'code' and explain it.\n"
        "If it's a plant, pick 'plant'. If a bicycle, pick 'bicycle'. Else 'other'.\n"
        f"Write all natural-language text in this locale: {out_lang}.\n"
        "Return STRICT JSON with keys ONLY:\n"
        "{\n"
        "  'domain': 'circuit|plant|code|bicycle|other',\n"
        "  'labels': ['tag1','tag2'],\n"
        "  'summary': '1-3 sentence description in the target language',\n"
        "  'explanation': 'if code: what it does; else helpful facts, in the target language',\n"
        "  'language': 'if code, language guess (e.g., Python) else null'\n"
        "}"
    )

    resp = model.generate_content([prompt, pil_img], request_options={"timeout": 30})
    text = ""
    try:
        text = resp.text or ""
    except Exception:
        try:
            text = "\n".join(
                p.text for p in resp.candidates[0].content.parts if getattr(p, "text", None)
            )
        except Exception:
            text = ""
    data = _extract_json(text)
    if not data:
        data = {
            "domain": "other",
            "labels": [],
            "summary": text.strip()[:600] or i18n.t("ar.no_text", "No textual response."),
            "explanation": "",
            "language": None,
        }
    return data

# --- concept mapping into your content pack ---
CONCEPT_MAP = {"circuit": "circuit_basics", "plant": "plant_basics", "bicycle": "bicycle"}

def show_concept(concept_key: str):
    try:
        concepts = json.load(open("data/concepts.json", "r", encoding="utf-8"))
        c = concepts.get(concept_key)
        if not c:
            st.info(i18n.t("ar.no_concept", "No mapped concept content yet."))
            return
        with st.expander("📌 " + c.get("title", "Concept"), expanded=True):
            for k in c.get("key_ideas", []):
                st.write("• " + k)
            if c.get("video") and c.get("captions"):
                st.write("### " + i18n.t("ar.explainer", "Explainer Video"))
                video.render_video_with_transcript(c["video"], c["captions"], auto_open=True)
            a11y.tts_button(i18n.t("ar.tts_intro", "Here are key ideas related to the detected concept."))
    except Exception:
        st.info(i18n.t("ar.concept_error", "Concept content not available (check data/concepts.json)."))

# ---- main flow ----
img_bgr = None
if uploaded:
    file_bytes = np.frombuffer(uploaded.read(), np.uint8)
    img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
elif cam:
    file_bytes = np.frombuffer(cam.getvalue(), np.uint8)
    img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

if img_bgr is not None:
    st.image(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB),
             caption=i18n.t("ar.input", "Input"),
             use_container_width=True)

    used_ai = False
    try:
        pil = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
        result = ai_describe_image(pil, LANG)
        used_ai = True

        st.subheader(i18n.t("ar.ai_analysis", "AR Analysis"))
        st.write(f"**{i18n.t('ar.domain','Domain')}:** {result.get('domain')}")
        if result.get("labels"):
            st.write("**" + i18n.t("ar.tags", "Tags") + ":** " + ", ".join(result["labels"]))
        if result.get("summary"):
            st.markdown("**" + i18n.t("ar.summary", "Summary") + ":** " + result["summary"])
        if result.get("explanation"):
            st.markdown("**" + i18n.t("ar.explanation", "Explanation") + ":** " + result["explanation"])
        if result.get("language"):
            st.caption(i18n.t("ar.language", "Language") + f": {result['language']}")
        a11y.tts_button(f"{result.get('summary','')}. {result.get('explanation','')}")

        ckey = CONCEPT_MAP.get(result.get("domain"))
        if ckey:
            show_concept(ckey)

    except Exception:
        used_ai = False
        st.info(i18n.t("ar.fallback", "AR analysis unavailable; using offline detector."))

    if not used_ai:
        try:
            res = arutil.detect_any(img_bgr, json_path="data/templates.json")
            if res["found"]:
                if res["type"] == "qr":
                    st.success(i18n.t("ar.detected_qr", "QR code detected."))
                    st.write("**Data:**", res["meta"].get("data", ""))
                    if res.get("concept_key"):
                        show_concept(res["concept_key"])
                elif res["type"] == "template":
                    meta = res["meta"].get("meta", {})
                    score = res["meta"].get("score")
                    st.success(i18n.t("ar.detected_template", "Template detected.") +
                               f" **{meta.get('title','Marker')}** (score: {score})")
                    if meta.get("concept_key"):
                        show_concept(meta["concept_key"])
                elif res["type"] == "heuristic":
                    st.info(i18n.t("ar.detected_heur", "Heuristic match") + f": **{res['label']}**")
                    if res.get("concept_key"):
                        show_concept(res["concept_key"])
                else:
                    st.info(i18n.t("ar.no_match", "No detection."))
            else:
                r2 = arutil.detect_marker(img_bgr, "data/bicycle_marker.png")
                st.write(i18n.t("ar.score", "Detection score") + f": {r2.get('score', 0):.2f}")
                if r2.get("found"):
                    show_concept("bicycle")
                else:
                    st.info(i18n.t("ar.no_match2", "No QR/marker/heuristic match."))
        except Exception:
            st.info(i18n.t("ar.offline_na", "Offline detector not available."))
else:
    st.caption(i18n.t("ar.tip", "Tip: try a circuit diagram, plant photo, code screenshot, or the bicycle marker."))
