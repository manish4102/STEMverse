# utils/paths.py
import os, tempfile
from functools import lru_cache
from pathlib import Path

@lru_cache()
def db_path() -> str:
    candidate = os.getenv("STEMVERSE_DB", os.path.join("db", "stemverse.sqlite"))
    dirn = os.path.dirname(candidate) or "."
    try:
        os.makedirs(dirn, exist_ok=True)
        if os.access(dirn, os.W_OK):
            return candidate
    except Exception:
        pass
    return os.path.join(tempfile.gettempdir(), "stemverse.sqlite")

DB_PATH = db_path()

# NEW: resolve paths relative to the app folder (this file lives in app/utils/)
@lru_cache()
def app_root() -> Path:
    return Path(__file__).resolve().parents[1]  # .../app

def data_path(*parts) -> str:
    return str(app_root() / "data" / Path(*parts))

def asset_path(*parts) -> str:
    # alias if you keep videos/captions under app/data as well
    return str(app_root() / Path(*parts))
