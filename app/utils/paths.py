# utils/paths.py
import os, tempfile
from functools import lru_cache

@lru_cache()
def db_path() -> str:
    # Allow override; useful for Cloud if you ever want to pin a path.
    candidate = os.getenv("STEMVERSE_DB", os.path.join("db", "stemverse.sqlite"))
    dirn = os.path.dirname(candidate) or "."

    # If the directory is writable, use it
    try:
        os.makedirs(dirn, exist_ok=True)
        if os.access(dirn, os.W_OK):
            return candidate
    except Exception:
        pass

    # Fallback to /tmp (always writable on Streamlit Cloud)
    return os.path.join(tempfile.gettempdir(), "stemverse.sqlite")

DB_PATH = db_path()
