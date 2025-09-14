
# STEMverse Together

A multi-page Streamlit app with co‑op games, accessibility, and rewards.
Run locally with:

```bash
pip install streamlit pandas numpy opencv-python Pillow plotly pyttsx3
cd app
streamlit run Home.py
```

## Structure
- `pages/` – individual mini-apps
- `data/` – seed JSON + assets (videos are placeholders; app falls back to transcript)
- `db/` – SQLite file auto-created on first run
- `utils/` – helpers (a11y, AR, wallet, etc.)

## Awards
- Treasure Hunt: 100 coins per level (3 levels)
- Heads Up: +10 coins per correct term
- Escape Room: +50 coins (first solve only)
