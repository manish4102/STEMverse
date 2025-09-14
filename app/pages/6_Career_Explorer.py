# pages/7_Roadmap_Quiz.py
import os
import streamlit as st
from utils.paths import DB_PATH

# -------------------------------
# Quiz (your original logic)
# -------------------------------
st.title("🧭 Roadmap Quiz (Optional)")
qs = [
    ("I enjoy logic puzzles.", "logic"),
    ("I like math problems.", "math"),
    ("I prefer building things.", "hands_on"),
    ("I'm curious about circuits.", "logic"),
    ("I like coding small games.", "logic"),
]
scores = {"logic": 0, "math": 0, "hands_on": 0}

with st.form("quiz"):
    for q, cat in qs:
        val = st.slider(q, 0, 2, 1)
        scores[cat] += val
    if st.form_submit_button("Get Path"):
        st.session_state["rm_scores"] = scores

sc = st.session_state.get("rm_scores")
if sc:
    st.subheader("Recommended 3-step path")
    if sc["logic"] >= sc["math"] and sc["logic"] >= sc["hands_on"]:
        path = ["Intro to Circuits", "Basic Algorithms", "Logic Games"]
        strongest = "logic"
    elif sc["math"] >= sc["hands_on"]:
        path = ["Number Sense", "Algebra Basics", "Data Patterns"]
        strongest = "math"
    else:
        path = ["Maker Basics", "Arduino Intro", "Build & Test"]
        strongest = "hands_on"
    for i, mod in enumerate(path, 1):
        st.write(f"{i}. {mod}")
    st.download_button("Export as text", "\n".join(path))
else:
    strongest = None

# ---------------------------------------
# Career Gallery — dropdown cards (3/row)
# ---------------------------------------
st.divider()
st.header("🎓 Career Gallery")

IMG_DIR = "data/career_images"
os.makedirs(IMG_DIR, exist_ok=True)

EMO = {
    "astronaut": "🧑‍🚀",
    "chemist": "🧪",
    "computer_programmer": "💻",
    "marine_biologist": "🐠",
    "tutor": "🧑‍🏫",
    "accountant": "📊",
    "architect": "🏛️",
    "interior_designer": "🛋️",
}

CAREERS = [
    {
        "id": "astronaut",
        "name": "Astronaut",
        "about": "Lives and works in space conducting experiments, maintenance, and exploration tasks.",
        "skills": [
            "Physics & engineering basics", "Robotics/EVA procedures", "Physical fitness",
            "Teamwork", "Calm problem-solving"
        ],
        "day": [
            "Mission briefing & timeline review",
            "Exercise for microgravity health",
            "Run science experiments / log results",
            "Station maintenance or spacewalk prep",
            "Comms with mission control & daily report"
        ],
        "default_image": f"/Users/manish/Downloads/app/data/career_images/Astronaut.jpg",
    },
    {
        "id": "chemist",
        "name": "Chemist",
        "about": "Studies substances and reactions to develop materials, medicines, and analytical methods.",
        "skills": [
            "Lab safety & SOPs", "Stoichiometry & reaction mechanisms",
            "Instrumentation (GC/MS, NMR, UV-Vis)", "Data analysis", "Documentation"
        ],
        "day": [
            "Plan experiments & prepare reagents",
            "Run reactions / instrument analyses",
            "Record data & interpret spectra",
            "Troubleshoot procedures and yields",
            "Write reports and discuss results"
        ],
        "default_image": f"/Users/manish/Downloads/app/data/career_images/Chemist.jpg",
    },
    {
        "id": "computer_programmer",
        "name": "Computer Programmer",
        "about": "Writes and maintains code for apps, games, tools, and backend services.",
        "skills": [
            "Python/JS or another language", "Algorithms & data structures",
            "Version control (Git)", "Testing & debugging", "Clear communication"
        ],
        "day": [
            "Stand-up & task review",
            "Implement features and write tests",
            "Code reviews with teammates",
            "Fix bugs & refactor",
            "Plan next sprint items"
        ],
        "default_image": f"/Users/manish/Downloads/app/data/career_images/Computer_Programmer.jpg",
    },
    {
        "id": "marine_biologist",
        "name": "Marine Biologist",
        "about": "Researches ocean organisms, ecosystems, and conservation using field and lab methods.",
        "skills": [
            "Biology/ecology", "Fieldwork & sampling", "Data analysis (R/Python)",
            "Diving/boating safety (where applicable)", "Scientific writing"
        ],
        "day": [
            "Survey or sampling in the field",
            "Process samples / lab measurements",
            "Analyze datasets & visualize trends",
            "Team meeting on conservation insights",
            "Draft manuscripts or reports"
        ],
        "default_image": f"/Users/manish/Downloads/app/data/career_images/Marine_Biologist.jpg",
    },
    {
        "id": "tutor",
        "name": "Tutor",
        "about": "Helps learners master subjects through explanation, practice, and feedback.",
        "skills": [
            "Subject mastery", "Instructional strategies", "Patience & empathy",
            "Assessment & feedback", "Communication"
        ],
        "day": [
            "Review learner goals & progress",
            "Explain concepts with examples",
            "Guide practice problems",
            "Assess understanding & adjust plan",
            "Share summary & next steps"
        ],
        "default_image": f"/Users/manish/Downloads/app/data/career_images/Tutor.jpg",
    },
    {
        "id": "accountant",
        "name": "Accountant",
        "about": "Prepares and analyzes financial records to ensure accuracy and compliance.",
        "skills": [
            "Accounting principles (GAAP/IFRS)", "Excel/Sheets & accounting software",
            "Attention to detail", "Data analysis", "Tax/regulatory knowledge"
        ],
        "day": [
            "Reconcile accounts & transactions",
            "Prepare statements or filings",
            "Analyze variances & trends",
            "Meet with clients/stakeholders",
            "Document controls & procedures"
        ],
        "default_image": f"/Users/manish/Downloads/app/data/career_images/Accountant.jpg",
    },
    {
        "id": "architect",
        "name": "Architect",
        "about": "Designs buildings that balance aesthetics, structure, sustainability, and code requirements.",
        "skills": [
            "Concept design & sketching", "CAD/BIM (Revit/AutoCAD)",
            "Structures & materials", "Building codes", "Client communication"
        ],
        "day": [
            "Client/consultant meetings",
            "Concept sketches & iterations",
            "BIM modeling & detailing",
            "Coordination with engineers",
            "Site visits & documentation"
        ],
        "default_image": f"/Users/manish/Downloads/app/data/career_images/Architect.jpg",
    },
    {
        "id": "interior_designer",
        "name": "Interior Designer",
        "about": "Plans interior spaces, materials, and lighting to meet function, safety, and style goals.",
        "skills": [
            "Space planning", "Materials & finishes", "Lighting design",
            "CAD/rendering tools", "Client collaboration"
        ],
        "day": [
            "Mood boards & concept refinement",
            "Floor plans & 3D mockups",
            "Material/finish selection",
            "Vendor coordination & budgets",
            "Walkthroughs & revisions"
        ],
        "default_image": f"/Users/manish/Downloads/app/data/career_images/Interior_Designer.jpg",
    },
]

def recommended_ids(strength: str):
    if strength == "logic":
        return ["computer_programmer", "architect", "accountant"]
    if strength == "math":
        return ["accountant", "chemist", "computer_programmer"]
    return ["astronaut", "marine_biologist", "interior_designer"]

if strongest:
    st.caption(f"⭐ Recommended careers for **{strongest.replace('_',' ')}** are marked with a star.")

# Keep user-chosen image paths this session
st.session_state.setdefault("career_image_paths", {})

def _img_for(career):
    override = st.session_state["career_image_paths"].get(career["id"])
    path = override or career["default_image"]
    return path if (path and os.path.exists(path)) else None

def chunk3(lst):
    for i in range(0, len(lst), 3):
        yield lst[i:i+3]

# Render dropdown cards (3 per row)
for row in chunk3(CAREERS):
    cols = st.columns(len(row), gap="large")
    for col, c in zip(cols, row):
        with col:
            emoji = EMO.get(c["id"], "🗂️")
            star = " ⭐" if strongest and c["id"] in recommended_ids(strongest) else ""
            # Only this one line is visible when collapsed:
            with st.expander(f"{emoji} {c['name']}{star}", expanded=False):
                img_path = _img_for(c)
                if img_path:
                    st.image(img_path, use_container_width=True, caption=c["name"])
                else:
                    st.info(
                        "No image yet. Add one below or place a file at:\n\n"
                        f"`{c['default_image']}`"
                    )

                st.markdown(f"**What it’s about:** {c['about']}")
                st.markdown("**Skills you’ll need:**")
                for sskill in c["skills"]:
                    st.write("• " + sskill)
                st.markdown("**A day in the life:**")
                for step in c["day"]:
                    st.write("• " + step)

                st.markdown("---")
                st.markdown("**Set image**")
                path_in = st.text_input(
                    "Path to an image file",
                    value=st.session_state["career_image_paths"].get(c["id"], c["default_image"]),
                    key=f"path_{c['id']}",
                )
                if st.button("Use path", key=f"use_{c['id']}"):
                    st.session_state["career_image_paths"][c["id"]] = path_in
                    st.rerun()

                up = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"], key=f"up_{c['id']}")
                if up:
                    ext = os.path.splitext(up.name)[1].lower() or ".png"
                    save_path = os.path.join(IMG_DIR, f"{c['id']}{ext}")
                    with open(save_path, "wb") as f:
                        f.write(up.read())
                    st.session_state["career_image_paths"][c["id"]] = save_path
                    st.success(f"Saved to {save_path}")
                    st.rerun()


