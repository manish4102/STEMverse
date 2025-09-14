# utils/paths.py
import os, tempfile
from functools import lru_cache

@lru_cache()
def db_path() -> str:
    # Allow override via env, else prefer repo ./db/stemverse.sqlite
    candidate = os.getenv("STEMVERSE_DB", os.path.join("db", "stemverse.sqlite"))
    dirn = os.path.dirname(candidate)

    # If the directory exists AND is writable, use it
    if dirn and os.path.isdir(dirn) and os.access(dirn, os.W_OK):
        return candidate

    # Try to create it if possible
    try:
        if dirn:
            os.makedirs(dirn, exist_ok=True)
            if os.access(dirn, os.W_OK):
                return candidate
    except Exception:
        pass

    # Fallback to a guaranteed writable temp location on Streamlit Cloud
    return os.path.join(tempfile.gettempdir(), "stemverse.sqlite")

DB_PATH = db_path()
