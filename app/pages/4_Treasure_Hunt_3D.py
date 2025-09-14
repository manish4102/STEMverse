# pages/4_Treasure_Hunt_3D.py
# Three noir-style treasure hunts with topic cards → scene → 4 sequential clues → LED lock → +100 coins.

import streamlit as st
from utils import wallet, state, i18n, layout, a11y

DB_PATH = "db/stemverse.sqlite"
AWARD_COINS = 100  # reward per case

st.set_page_config(page_title="Treasure Hunt", layout="wide")

# Language/Session bootstrap
uid = state.get_user_id()
i18n.init_from_session_or_db(default="en-US", db_path=DB_PATH, uid=uid)

# Sidebar (same across pages)
with st.sidebar:
    settings = layout.render_sidebar(DB_PATH, uid)  # includes lang_code, reduced_motion, tts, etc.

# -----------------------------
# Define the three cases
# -----------------------------
SCENARIOS = [
    {
        "id": "case_lab",
        "title": "Case 1 — Lab After Hours",
        "topics": ["Physics", "Circuits", "Chemistry", "Binary"],
        "scene": (
            "**Night hums in the engineering lab.** Emergency lights flicker; a locker door hangs open.\n"
            "A note by the soldering station reads: *“Four clues, one lock. Mind the circuits.”*"
        ),
        "clues": [
            {
                "type": "text",
                "title": "Clue 1 — Force at a Distance",
                "prompt": "I push without touching. What am I?",
                "answer": "magnet",
                "hints": ["Think invisible fields.", "It can deflect a compass needle."]
            },
            {
                "type": "mcq",
                "title": "Clue 2 — Powering the LED",
                "prompt": "Two identical batteries and one LED (safe limits). Which setup makes the LED brighter?",
                "options": [
                    "Batteries in parallel (same voltage, more capacity)",
                    "Batteries in series (higher voltage)",
                    "Either is the same"
                ],
                "answer": "Batteries in series (higher voltage)",
                "hints": ["LED current depends on voltage across it.", "Series increases voltage."]
            },
            {
                "type": "text",
                "title": "Clue 3 — Binary Whisper",
                "prompt": "Decode this ASCII binary: **01100001 01101001**",
                "answer": "ai",
                "hints": ["8-bit chunks → ASCII table.", "It's a two-letter tech acronym."]
            },
            {
                "type": "text",
                "title": "Clue 4 — Chemistry Scramble",
                "prompt": "Unscramble: **TCAAYLTS** (hint: speeds reactions)",
                "answer": "catalyst",
                "hints": ["Ends with “...lyst”.", "Lowers activation energy."]
            },
        ],
        "lock_target": "1010"  # ON, OFF, ON, OFF
    },
    {
        "id": "case_green",
        "title": "Case 2 — Greenhouse Riddle",
        "topics": ["Biology", "Chemistry", "Math", "Data"],
        "scene": (
            "Warm air fogs the greenhouse glass. A clipboard lists plant stats and a cryptic doodle of a leaf.\n"
            "A sticky note says: *“Nature keeps the books—if you can read them.”*"
        ),
        "clues": [
            {
                "type": "text",
                "title": "Clue 1 — Sunlit Kitchen",
                "prompt": "Name the process: plants make food from CO₂ and water using light.",
                "answer": "photosynthesis",
                "hints": ["Photo + synthesis.", "It produces glucose and O₂."]
            },
            {
                "type": "mcq",
                "title": "Clue 2 — Tiny Doors",
                "prompt": "Which leaf structure mainly controls gas exchange?",
                "options": ["Xylem", "Phloem", "Stomata", "Cuticle"],
                "answer": "Stomata",
                "hints": ["They open/close on the epidermis.", "Guard cells control them."]
            },
            {
                "type": "text",
                "title": "Clue 3 — Quick Growth Math",
                "prompt": "A plant doubles its leaves each day for 3 days, starting with 2 leaves. Total?",
                "answer": "16",
                "hints": ["2 × 2³.", "2, 4, 8, 16..."]
            },
            {
                "type": "mcq",
                "title": "Clue 4 — Chemistry Note",
                "prompt": "Soil with pH 5.8 is…",
                "options": ["Acidic", "Neutral", "Basic"],
                "answer": "Acidic",
                "hints": ["Neutral is 7.", "< 7 is acidic."]
            },
        ],
        "lock_target": "1100"  # ON, ON, OFF, OFF
    },
    {
        "id": "case_astro",
        "title": "Case 3 — Astro Array Heist",
        "topics": ["Space", "CS", "Logic", "Physics"],
        "scene": (
            "At the radio array control room, a console blinks with logs and a star map.\n"
            "A scrawl on a printout: *“Tune to truth; decode the silence.”*"
        ),
        "clues": [
            {
                "type": "mcq",
                "title": "Clue 1 — Orbits 101",
                "prompt": "Kepler’s 3rd law relates a planet’s orbital period to the…",
                "options": ["Planet mass", "Semi-major axis of its orbit", "Stellar temperature"],
                "answer": "Semi-major axis of its orbit",
                "hints": ["T² ∝ a³.", "Distance matters more than the planet’s mass."]
            },
            {
                "type": "text",
                "title": "Clue 2 — Hex Ping",
                "prompt": "Decode this ASCII hex: **41 49**",
                "answer": "ai",
                "hints": ["41='A', 49='I' in ASCII hex.", "Two letters; same as in binary clue you’ve seen."]
            },
            {
                "type": "text",
                "title": "Clue 3 — Signal Logic",
                "prompt": "A band-pass filter lets through frequencies around a center and rejects others. One word answer:",
                "answer": "bandpass",
                "hints": ["Think ‘band’ + ‘pass’.", "One word, no hyphen."]
            },
            {
                "type": "mcq",
                "title": "Clue 4 — Gears in Space?",
                "prompt": "A **gear ratio** greater than 1 generally gives…",
                "options": ["More speed, less torque", "More torque, less speed", "Both more torque and speed"],
                "answer": "More torque, less speed",
                "hints": ["Trade-off.", "Big ratio favors torque."]
            },
        ],
        "lock_target": "0110"  # OFF, ON, ON, OFF
    }
]

# -----------------------------
# Session state
# -----------------------------
if "th_selected" not in st.session_state:
    st.session_state["th_selected"] = None  # scenario id or None
if "th_step" not in st.session_state:
    st.session_state["th_step"] = 0         # 0 scene, 1..4 clues, 5 lock, 6 done
if "th_solved" not in st.session_state:
    st.session_state["th_solved"] = {}      # {scenario_id: [bool,bool,bool,bool]}
if "th_hints" not in st.session_state:
    st.session_state["th_hints"] = {}       # {scenario_id: [2,2,2,2]}

def _ensure_state(sid: str):
    st.session_state["th_solved"].setdefault(sid, [False, False, False, False])
    st.session_state["th_hints"].setdefault(sid, [2, 2, 2, 2])

def _reset_all():
    st.session_state["th_selected"] = None
    st.session_state["th_step"] = 0

def _start_case(sid: str):
    st.session_state["th_selected"] = sid
    st.session_state["th_step"] = 0
    _ensure_state(sid)

def _next_step():
    st.session_state["th_step"] += 1

# -----------------------------
# Topic cards (picker)
# -----------------------------
if st.session_state["th_selected"] is None:
    st.title("🗺️ " + i18n.t("th.title", "Treasure Hunt — Choose Your Case"))
    st.caption(i18n.t(
        "th.pick_caption",
        "Pick a case. Each card shows the STEM topics you’ll use. Solve 4 clues, then crack the LED lock for +100 coins."
    ))
    cols = st.columns(3)
    for i, sc in enumerate(SCENARIOS):
        with cols[i]:
            try:
                with st.container(border=True):
                    st.subheader(sc["title"])
                    st.write("**" + i18n.t("th.topics_tested", "Topics tested:") + "**")
                    st.write(" • " + "\n • ".join(sc["topics"]))
                    st.button(i18n.t("th.start", "Start ▶️"),
                              key=f"start_{sc['id']}",
                              use_container_width=True,
                              on_click=_start_case, args=(sc["id"],))
            except TypeError:
                # Older Streamlit without container(border=...)
                st.subheader(sc["title"])
                st.write("**" + i18n.t("th.topics_tested", "Topics tested:") + "**")
                st.write(" • " + "\n • ".join(sc["topics"]))
                st.button(i18n.t("th.start", "Start ▶️"),
                          key=f"start_{sc['id']}",
                          use_container_width=True,
                          on_click=_start_case, args=(sc["id"],))
    st.stop()

# -----------------------------
# Active case flow
# -----------------------------
case = next(s for s in SCENARIOS if s["id"] == st.session_state["th_selected"])
sid = case["id"]
_ensure_state(sid)

st.markdown(f"### {case['title']}")
st.write("**" + i18n.t("th.topics", "Topics:") + f"** {', '.join(case['topics'])}")

# Scene (step 0)
if st.session_state["th_step"] == 0:
    st.info(case["scene"])
    if settings.get("tts"):
        a11y.tts_button(case["scene"], key=f"tts_scene_{sid}")
    c1, c2 = st.columns([1,1])
    with c1:
        st.button(i18n.t("th.begin", "Begin ▶️"),
                  use_container_width=True, on_click=_next_step)
    with c2:
        st.button(i18n.t("th.back_cases", "Back to cases"),
                  use_container_width=True, on_click=_reset_all)
    st.stop()

# Clues (steps 1..4)
curr = st.session_state["th_step"]
if 1 <= curr <= 4:
    i = curr - 1
    clue = case["clues"][i]
    st.subheader(clue["title"])
    st.write(clue["prompt"])
    if settings.get("tts"):
        a11y.tts_button(clue["prompt"], key=f"tts_clue_{sid}_{i}")

    # Answer input
    if clue["type"] == "text":
        ans = st.text_input(i18n.t("th.your_answer", "Your answer"), key=f"ans_{sid}_{i}")
    else:
        ans = st.radio(i18n.t("th.choose_one", "Choose one:"), options=clue["options"], key=f"ans_{sid}_{i}")

    colA, colB, colC = st.columns([1,1,1])

    def _check():
        val = (ans or "").strip()
        if clue["type"] == "text":
            ok = val.lower() == clue["answer"].lower()
        else:
            ok = val == clue["answer"]
        if ok:
            st.session_state["th_solved"][sid][i] = True
            st.success(i18n.t("th.correct", "Correct! Moving on…"))
            _next_step()
        else:
            st.error(i18n.t("th.try_again", "Not quite. Try again."))

    def _hint():
        left = st.session_state["th_hints"][sid][i]
        if left > 0:
            idx = 2 - left
            tip = clue["hints"][min(idx, len(clue["hints"]) - 1)]
            st.info(tip)
            st.session_state["th_hints"][sid][i] -= 1
        else:
            st.warning(i18n.t("th.no_hints", "No hints left for this clue."))

    with colA:
        st.button(i18n.t("th.check", "Check"), use_container_width=True, on_click=_check)
    with colB:
        st.button(i18n.t("th.hint", "Hint"), use_container_width=True, on_click=_hint)
    with colC:
        st.button(i18n.t("th.back_cases", "Back to cases"),
                  use_container_width=True, on_click=_reset_all)

    # Progress
    solved = st.session_state["th_solved"][sid]
    st.progress(int(100 * (sum(solved) / 4)),
                text=i18n.t("th.progress", "Clues solved: {n}/4", n=sum(solved)))
    st.stop()

# LED Lock (step 5)
if curr == 5:
    st.subheader(i18n.t("th.final_lock", "Final Lock — LED Pattern"))
    st.caption(i18n.t("th.final_lock_caption", "Match the target LED states to open the treasure."))
    target = case["lock_target"]
    toggles = []
    for j in range(4):
        # Accessible labels; include target state for clarity
        target_txt = i18n.t("th.target_on", "ON") if target[j] == "1" else i18n.t("th.target_off", "OFF")
        label = i18n.t("th.led_label", "LED {k}: target {state}", k=j+1, state=target_txt)
        toggles.append(st.toggle(label, key=f"led_{sid}_{j}"))
    pattern = "".join("1" if v else "0" for v in toggles)
    st.write(i18n.t("th.current_pattern", "Current pattern: **{cur}** | Target: **{tar}**",
                    cur=pattern, tar=target))

    wallet.ensure_wallet(DB_PATH, uid)

    if pattern == target:
        st.success(i18n.t("th.lock_open", "Lock released. The chest clicks open."))
        granted = wallet.add_coins(
            DB_PATH, uid, AWARD_COINS,
            i18n.t("th.reward_reason", "Treasure Hunt — {title} complete", title=case['title']),
            dedupe_key=f"TH_SEQ_{sid}_{uid}"
        )
        if granted and not settings.get("reduced_motion", False):
            st.balloons()
        st.info(i18n.t("th.earned", "You earned **+{coins} coins**.", coins=AWARD_COINS))
        st.session_state["th_step"] = 6
    else:
        st.info(i18n.t("th.toggle_to_match", "Toggle the switches to match the target."))

    st.button(i18n.t("th.back_cases", "Back to cases"),
              use_container_width=True, on_click=_reset_all)
    st.stop()

# Done (step 6)
st.success(i18n.t("th.done", "🎉 Treasure secured!"))
st.button(i18n.t("th.back_cases", "Back to cases"),
          use_container_width=True, on_click=_reset_all)
