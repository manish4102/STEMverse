# pages/8_Buddy_Program.py
import time, secrets, urllib.parse
import streamlit as st
from utils import buddy, state
from utils.paths import DB_PATH

DB = "db/stemverse.sqlite"
st.title("👥 Buddy Program")

# ----- helpers -----
def _gen_code():
    # 8 char, URL-safe, uppercase (e.g., STEM-AB3X)
    raw = secrets.token_urlsafe(6).upper().replace("-", "")
    return f"STEM-{raw[:4]}{raw[4:8]}"

def _join_room(code: str):
    rid = buddy.create_or_join_room(DB, code)
    st.session_state["room_id"] = rid
    st.session_state["room_code"] = code
    # put room code in URL so you can share the link
    try:
        st.experimental_set_query_params(room=code)
    except Exception:
        pass

def _send_msg():
    msg = st.session_state.get("chat_msg", "").strip()
    if msg and "room_id" in st.session_state:
        buddy.post_message(DB, st.session_state["room_id"], state.get_user_id(), msg)
    st.session_state["chat_msg"] = ""
    st.experimental_rerun()

# ----- URL auto-join -----
qp = {}
try:
    qp = st.experimental_get_query_params()
except Exception:
    pass
prefill = qp.get("room", [None])[0]

# ----- room code input & actions -----
left, mid, right = st.columns([1.6, 1, 1])
with left:
    code = st.text_input("Enter / Create room code", value=prefill or "STEM-1234AB", key="room_code_input")
with mid:
    if st.button("Create/Join Room", use_container_width=True):
        _join_room(st.session_state["room_code_input"].strip())
with right:
    if st.button("Generate code", use_container_width=True):
        st.session_state["room_code_input"] = _gen_code()
        st.experimental_rerun()

# Auto-join when arriving with ?room=
if prefill and "room_id" not in st.session_state:
    _join_room(prefill)

# ----- role selection -----
role = st.selectbox("Choose role", ["Circuit Planner", "Switch Operator"])
if st.button("Confirm Role"):
    if "room_id" in st.session_state:
        buddy.add_member(DB, st.session_state["room_id"], state.get_user_id(), role)
        st.toast("Role saved.")

# ----- room UI if joined -----
if "room_id" in st.session_state:
    room_code = st.session_state.get("room_code", st.session_state.get("room_code_input", ""))
    st.info(f"Room: **{room_code}**")

    # Invite link (relative) and copy button
    invite_rel = f"?room={urllib.parse.quote(room_code)}"
    st.markdown(f"**Invite link:** [{invite_rel}]({invite_rel})")
    st.code(invite_rel, language="text")

    # Members
    st.write("**Members:**")
    for uid, r in buddy.list_members(DB, st.session_state["room_id"]):
        nm = uid[:8]
        st.write(f"• {nm} — {r}")

    # Mentor Ping
    ping_col, live_col = st.columns([1,1])
    with ping_col:
        if st.button("Mentor Ping"):
            buddy.post_message(DB, st.session_state["room_id"], "system", "Mentor ping requested.")
    with live_col:
        live = st.toggle("Auto-refresh chat (3s)", value=True)

    # Chat input (Enter to send)
    st.text_input("Chat message", key="chat_msg", on_change=_send_msg, placeholder="Type and press Enter…")

    # Auto-refresh (JS reload) if enabled
    if live:
        # lightweight refresh; preserves session state
        st.components.v1.html(
            "<script>setTimeout(()=>window.parent.location.reload(),3000)</script>",
            height=0, width=0
        )

    # Messages
    st.write("**Chat:**")
    for u, t, ts in buddy.get_messages(DB, st.session_state["room_id"]):
        short = (u[:6] if u != "system" else "system")
        st.write(f"{ts[:19]} [{short}]: {t}")

    st.divider()
    st.write("**Co-op Launchers**")
    st.page_link("pages/3_Heads_Up.py", label="Start Heads Up")
    st.page_link("pages/4_Treasure_Hunt_3D.py", label="Start Treasure Hunt (Co-op)")
else:
    st.info("Create or join a room to see members and chat.")
