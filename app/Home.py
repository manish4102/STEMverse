import os, json
import streamlit as st
from utils.paths import DB_PATH

from utils import a11y, state, db, wallet, i18n
from utils import layout  # <-- new import

DB_PATH = "db/stemverse.sqlite"
st.set_page_config(page_title="STEMverse", layout="wide")

# Seed translation files (safe no-op if present)
i18n.ensure_seed_files()

# Session user id
uid = state.get_user_id()

# Ensure language is initialized for this page (session or DB fallback)
i18n.init_from_session_or_db(default="en-US", db_path=DB_PATH, uid=uid)

# Sidebar (same on every page)
with st.sidebar:
    settings = layout.render_sidebar(DB_PATH, uid)

# User bootstrap
db.ensure_user(DB_PATH, uid)
if "profile_set" not in st.session_state:
    st.session_state["profile_set"] = False

st.title("🧪 " + i18n.t("home.title", "STEMverse Together"))
st.write(i18n.t("home.subtitle", "Co-op STEM mini-games with accessibility built-in."))

with st.form("profile"):
    nickname = st.text_input(i18n.t("profile.nickname", "Nickname"),
                             value=st.session_state.get("nickname",""))
    grade = st.selectbox(i18n.t("profile.grade", "Grade"),
                         ["4-5","6-8","9-10","11-12","Other"], index=1)
    if st.form_submit_button(i18n.t("profile.save", "Save Profile")):
        st.session_state["nickname"] = nickname
        st.session_state["profile_set"] = True
        # Persist prefs including the selected language from the sidebar
        db.update_prefs(
            DB_PATH, uid,
            tts_enabled=settings["tts"], high_contrast=settings["high_contrast"],
            large_text=settings["large_text"], reduced_motion=settings["reduced_motion"],
            captions_enabled=settings["captions"], transcript_enabled=settings["transcript"],
            lang=settings["lang_code"]
        )
        st.success(i18n.t("profile.saved", "Profile saved!"))

st.subheader(i18n.t("home.quick_start", "Quick Start"))
cols = st.columns(3)
with cols[0]:
    st.page_link("pages/1_AR_Scanner.py", label="🔎 " + i18n.t("nav.ar", "AR Scanner"))
    st.page_link("pages/3_Heads_Up.py", label="🧠 " + i18n.t("nav.heads_up", "Heads Up"))
with cols[1]:
    st.page_link("pages/4_Treasure_Hunt_3D.py", label="🗺️ " + i18n.t("nav.treasure", "Treasure Hunt 3D"))
    st.page_link("pages/5_AI_Tutor.py", label="🤖 " + i18n.t("nav.tutor", "AI Tutor"))
    st.page_link("pages/6_Career_Explorer.py", label="🚀 " + i18n.t("nav.careers", "Career Explorer"))
with cols[2]:
    st.page_link("pages/8_Buddy_Program.py", label="👥 " + i18n.t("nav.buddy", "Buddy Program"))
    st.page_link("pages/9_Admin_Content.py", label="🛠️ " + i18n.t("nav.admin", "Admin Content"))

st.divider()
st.write("**" + i18n.t(
    "home.demo_checklist",
    "Demo checklist: Create a profile → Toggle accessibility → Try AR Scanner → Earn coins → Play Heads Up → Clear Treasure Hunt levels → Explore careers."
) + "**")
