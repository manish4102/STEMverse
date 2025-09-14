
import streamlit as st, json, os

st.title("🛠️ Admin Content (JSON CRUD)")
files = {
    "concepts.json":"data/concepts.json",
    "terms.json":"data/terms.json",
    "treasure_hunt.json":"data/treasure_hunt.json",
    "puzzles.json":"data/puzzles.json",
    "careers.json":"data/careers.json"
}
sel = st.selectbox("Select file", list(files.keys()))
path = files[sel]
data = json.load(open(path,"r"))
st.code(json.dumps(data, indent=2), language="json")
new = st.text_area("Edit JSON", json.dumps(data, indent=2), height=300)
if st.button("Save"):
    try:
        obj = json.loads(new)
        json.dump(obj, open(path,"w"), indent=2)
        st.success("Saved.")
    except Exception as e:
        st.error(f"Invalid JSON: {e}")
