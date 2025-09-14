# pages/3_Heads_Up.py
import json, random
import streamlit as st

from utils import state, wallet, a11y, i18n, layout
from utils.paths import DB_PATH

DB_PATH = "db/stemverse.sqlite"
st.set_page_config(page_title="Heads Up", layout="wide")

# ---- Language/Session bootstrap ----
uid = state.get_user_id()
i18n.init_from_session_or_db(default="en-US", db_path=DB_PATH, uid=uid)

# ---- Sidebar (same on all pages) ----
with st.sidebar:
    settings = layout.render_sidebar(DB_PATH, uid)  # returns lang_code, tts, etc.

# ---- Load terms ----
terms = json.load(open("data/terms.json", "r", encoding="utf-8"))

st.title("🧠 " + i18n.t("heads.title", "Heads Up"))

# Localized mode labels but keep internal keys
MODE_OPTS = [("solo", i18n.t("heads.solo", "Solo")),
             ("buddy", i18n.t("heads.buddy", "Buddy"))]
mode_label = st.radio(i18n.t("heads.mode", "Mode"),
                      [label for _, label in MODE_OPTS],
                      horizontal=True)
mode = next(key for key, label in MODE_OPTS if label == mode_label)

difficulty = st.selectbox(i18n.t("heads.difficulty", "Difficulty"),
                          ["easy", "medium", "hard"], index=0)

# Keep separate round state per difficulty; reset if language changed
round_key = f"hu_{difficulty}"
if (round_key not in st.session_state
    or st.session_state[round_key].get("lang") != i18n.get_language()):
    pool = terms.get(difficulty, [])[:]
    random.shuffle(pool)
    st.session_state[round_key] = {
        "pool": pool,
        "score": 0,
        "seen": set(),
        "time_left": 30,
        "lang": i18n.get_language(),
    }

# Controls row
col1, col2 = st.columns(2)
with col1:
    if st.button(i18n.t("heads.start", "Start / Restart"), use_container_width=True):
        pool = terms.get(difficulty, [])[:]
        random.shuffle(pool)
        st.session_state[round_key] = {
            "pool": pool,
            "score": 0,
            "seen": set(),
            "time_left": 30,
            "lang": i18n.get_language(),
        }
with col2:
    st.metric(i18n.t("heads.score", "Score"), st.session_state[round_key]["score"])

# Buddy info (optional)
if mode == "buddy":
    room_code = st.session_state.get("room_code")
    if room_code:
        st.info(i18n.t("heads.buddy_tip_with_room",
                       "Buddy mode: you’re in room **{room}**. Use the same page together.",
                       room=room_code))
    else:
        st.info(i18n.t("heads.buddy_tip",
                       "Buddy mode: join or create a room on the Buddy Program page, then return here."))

# Game loop
if st.session_state[round_key]["pool"]:
    term = st.session_state[round_key]["pool"][0]
    # Big readable term
    st.markdown(f"<div style='font-size:2rem;font-weight:700;margin:0.5rem 0'>{term}</div>", unsafe_allow_html=True)

    # Read aloud (browser TTS) if enabled in sidebar
    if settings.get("tts"):
        a11y.tts_button(term, key="tts_term")

    c1, c2 = st.columns(2)
    if c1.button("✅ " + i18n.t("heads.correct", "Correct"), use_container_width=True):
        if term not in st.session_state[round_key]["seen"]:
            st.session_state[round_key]["score"] += 1
            # Reward: +10 coins per correct (idempotent per user+term globally)
            wallet.ensure_wallet(DB_PATH, uid)
            wallet.add_coins(DB_PATH, uid, 10, "Heads Up correct", dedupe_key=f"HU_{uid}_{term}")
        st.session_state[round_key]["seen"].add(term)
        # Move to next term
        st.session_state[round_key]["pool"].pop(0)

    if c2.button("⏭️ " + i18n.t("heads.skip", "Skip"), use_container_width=True):
        # Rotate to back of the queue
        st.session_state[round_key]["pool"].append(st.session_state[round_key]["pool"].pop(0))
else:
    st.success(i18n.t("heads.complete", "Round complete!"))
