# utils/layout.py
# Shared sidebar for all pages: Accessibility + Language + Wallet
import streamlit as st
from utils import i18n, a11y, wallet

LANG_CHOICES = [
    ("English (US) 🇺🇸", "en-US"),
    ("Español (España) 🇪🇸", "es-ES"),
    ("Français 🇫🇷", "fr-FR"),
]

def render_sidebar(db_path: str, user_id: str):
    """Draw a consistent sidebar on every page and persist settings in session."""
    # Ensure we have a language set before rendering labels
    lang_now = st.session_state.get("a11y_lang", "en-US")
    i18n.set_language(lang_now)

    st.header(i18n.t("sidebar.accessibility", "Accessibility Center"))

    # Toggles (default from session if present)
    tts = st.toggle(i18n.t("sidebar.tts", "Screen Reader (Read Aloud)"),
                    value=st.session_state.get("a11y_tts", False))
    hc  = st.toggle(i18n.t("sidebar.high_contrast", "High Contrast"),
                    value=st.session_state.get("a11y_hc", False))
    lt  = st.toggle(i18n.t("sidebar.large_text", "Large Text"),
                    value=st.session_state.get("a11y_lt", False))
    rm  = st.toggle(i18n.t("sidebar.reduced_motion", "Reduced Motion"),
                    value=st.session_state.get("a11y_rm", False))
    cc  = st.toggle(i18n.t("sidebar.captions", "Captions"),
                    value=st.session_state.get("a11y_cc", True))
    tr  = st.toggle(i18n.t("sidebar.transcript", "Transcript panel"),
                    value=st.session_state.get("a11y_tr", True))

    # Language select
    labels = [label for label, _ in LANG_CHOICES]
    default_idx = next((i for i, (_, code) in enumerate(LANG_CHOICES)
                        if code == lang_now), 0)
    sel_label = st.selectbox(i18n.t("sidebar.language", "Language"),
                             labels, index=default_idx)
    lang_code = dict(LANG_CHOICES)[sel_label]
    st.session_state["a11y_lang"] = lang_code
    i18n.set_language(lang_code)

    # Apply global CSS
    a11y.inject_global_styles(hc, lt, rm)

    # Persist toggles in session for all pages
    st.session_state["a11y_tts"] = tts
    st.session_state["a11y_hc"]  = hc
    st.session_state["a11y_lt"]  = lt
    st.session_state["a11y_rm"]  = rm
    st.session_state["a11y_cc"]  = cc
    st.session_state["a11y_tr"]  = tr

    # Wallet summary
    st.divider()
    st.subheader("🎉 " + i18n.t("sidebar.wallet", "Wallet"))
    wallet.ensure_wallet(db_path, user_id)
    bal = wallet.get_balance(db_path, user_id)
    st.metric(i18n.t("sidebar.coins", "Coins"), bal)
    for amt, reason, ts in wallet.recent_transactions(db_path, user_id):
        st.write(f"{ts[:19]}: {amt:+} – {reason}")

    # Return current settings in case pages want them
    return {
        "lang_code": lang_code, "tts": tts, "high_contrast": hc, "large_text": lt,
        "reduced_motion": rm, "captions": cc, "transcript": tr, "balance": bal
    }
