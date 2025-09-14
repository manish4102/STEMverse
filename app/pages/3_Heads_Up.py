# pages/3_Heads_Up.py
import json, random
import streamlit as st

from utils import state, wallet, a11y, i18n, layout
from utils.paths import DB_PATH, data_path

st.set_page_config(page_title="Heads Up", layout="wide")

# Bootstrap language and sidebar
uid = state.get_user_id()
i18n.init_from_session_or_db(default="en-US", db_path=DB_PATH, uid=uid)
with st.sidebar:
    settings = layout.render_sidebar(DB_PATH, uid)

# ---- robust terms loader ----
def _load_terms():
    path = data_path("terms.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # minimal shape check
        for k in ("easy", "medium", "hard"):
            data.setdefault(k, [])
        return data
    except Exception as e:
        st.warning(f"Could not load terms.json at {path}. Using a small fallback set. ({type(e).__name__})")
        return {
            "easy":   ["force", "mass", "energy", "atom", "circuit"],
            "medium": ["torque", "resistor", "momentum", "enzyme", "binary"],
            "hard":   ["entropy", "superposition", "oxidation", "algorithm", "telescope"],
        }

terms = _load_terms()  # <-- guaranteed to exist

st.title("🧠 " + i18n.t("heads.title", "Heads Up"))

# Mode & difficulty
mode = st.radio(i18n.t("heads.mode", "Mode"), [i18n.t("heads.solo","Solo"), i18n.t("heads.buddy","Buddy")], horizontal=True)
difficulty = st.selectbox(i18n.t("heads.difficulty","Difficulty"), ["easy","medium","hard"], index=0)

# In buddy mode, give a hint about the Buddy page (optional)
if mode != i18n.t("heads.solo","Solo"):
    room = st.session_state.get("room_code") or st.session_state.get("room_code_input")
    if room:
        st.info(i18n.t("heads.buddy_tip_with_room", "Buddy mode: you’re in room **{room}**. Use the same page together.", room=room))
    else:
        st.info(i18n.t("heads.buddy_tip", "Buddy mode: join or create a room on the Buddy Program page, then return here."))

# Round state per difficulty
round_key = f"round_{difficulty}"
if round_key not in st.session_state:
    pool = list(terms.get(difficulty, []))  # copy
    random.shuffle(pool)
    st.session_state[round_key] = {"pool": pool, "score": 0, "seen": set()}

col1, col2 = st.columns(2)
with col1:
    if st.button(i18n.t("heads.start","Start / Restart")):
        pool = list(terms.get(difficulty, []))
        random.shuffle(pool)
        st.session_state[round_key] = {"pool": pool, "score": 0, "seen": set()}
with col2:
    st.metric(i18n.t("heads.score","Score"), st.session_state[round_key]["score"])

# Main play area
state_obj = st.session_state[round_key]
if state_obj["pool"]:
    term = state_obj["pool"][0]
    st.header(term)
    if settings.get("tts"):
        a11y.tts_button(term, key="tts_term")

    c1, c2 = st.columns(2)

    def _mark_correct():
        # Award once per term per round
        if term not in state_obj["seen"]:
            state_obj["score"] += 1
            uid_local = state.get_user_id()
            wallet.ensure_wallet(DB_PATH, uid_local)
            wallet.add_coins(DB_PATH, uid_local, 10, "Heads Up correct", dedupe_key=f"HU_{uid_local}_{term}")
        state_obj["seen"].add(term)
        # move to next term
        state_obj["pool"].pop(0)

    def _skip():
        # rotate the term to the end
        state_obj["pool"].append(state_obj["pool"].pop(0))

    with c1:
        st.button("✅ " + i18n.t("heads.correct","Correct"), use_container_width=True, on_click=_mark_correct)
    with c2:
        st.button("⏭️ " + i18n.t("heads.skip","Skip"), use_container_width=True, on_click=_skip)

else:
    st.success(i18n.t("heads.complete","Round complete!"))
