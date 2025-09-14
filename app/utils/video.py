
import streamlit as st
import os

def parse_vtt(path):
    cues = []
    if not os.path.exists(path):
        return cues
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    start, end, text = None, None, []
    for ln in lines:
        if "-->" in ln:
            if start is not None:
                cues.append({"start":start, "end":end, "text":" ".join(text).strip()})
                text = []
            times = ln.split("-->")
            start = times[0].strip()
            end = times[1].strip()
        elif ln.strip() and not ln.startswith("WEBVTT"):
            text.append(ln.strip())
    if start is not None:
        cues.append({"start":start, "end":end, "text":" ".join(text).strip()})
    return cues

def render_video_with_transcript(video_path, vtt_path, auto_open=False):
    exists = os.path.exists(video_path) and os.path.getsize(video_path) > 24
    if exists:
        st.video(video_path)
    else:
        st.warning("Video file not found or placeholder. Showing transcript only.")
    cues = parse_vtt(vtt_path)
    if st.toggle("Show transcript", value=True or auto_open):
        for c in cues:
            st.write(f"**{c['start']}–{c['end']}** {c['text']}")
