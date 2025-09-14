# utils/db.py
import os, sqlite3
from typing import Optional, Dict, Any
from utils.paths import DB_PATH

# ---------- sqlite connector ----------

def _conn(db_path: str = DB_PATH) -> sqlite3.Connection:
    dirn = os.path.dirname(db_path) or "."
    try:
        os.makedirs(dirn, exist_ok=True)
    except Exception:
        pass

    conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
    except Exception:
        pass
    return conn

def _ensure_schema(conn: sqlite3.Connection):
    cur = conn.cursor()
    # Basic user identity
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            nickname TEXT,
            grade TEXT,
            lang TEXT,
            created_at TEXT
        )
    """)
    # UI/accessibility preferences (per user)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS prefs (
            user_id TEXT PRIMARY KEY,
            tts_enabled INTEGER DEFAULT 0,
            high_contrast INTEGER DEFAULT 0,
            large_text INTEGER DEFAULT 0,
            reduced_motion INTEGER DEFAULT 0,
            captions_enabled INTEGER DEFAULT 1,
            transcript_enabled INTEGER DEFAULT 1,
            lang TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()

# ---------- public API ----------

def ensure_user(db_path: str, user_id: str, nickname: str = "", grade: str = "Other", lang: str = "en-US"):
    """Create a user row if missing."""
    conn = _conn(db_path); _ensure_schema(conn)
    cur = conn.cursor()
    # Insert if not exists; use SQLite time to avoid Python datetime adapter issues on Cloud
    cur.execute(
        "INSERT OR IGNORE INTO users (id, nickname, grade, lang, created_at) "
        "VALUES (?, ?, ?, ?, datetime('now'))",
        (user_id, nickname, grade, lang)
    )
    conn.commit()
    conn.close()

def update_profile(db_path: str, user_id: str, nickname: Optional[str] = None,
                   grade: Optional[str] = None, lang: Optional[str] = None):
    """Update basic profile fields if provided."""
    conn = _conn(db_path); _ensure_schema(conn)
    cur = conn.cursor()
    # Ensure the user exists
    cur.execute("INSERT OR IGNORE INTO users (id, nickname, grade, lang, created_at) "
                "VALUES (?, '', 'Other', ?, datetime('now'))",
                (user_id, lang or "en-US"))
    if nickname is not None:
        cur.execute("UPDATE users SET nickname=? WHERE id=?", (nickname, user_id))
    if grade is not None:
        cur.execute("UPDATE users SET grade=? WHERE id=?", (grade, user_id))
    if lang is not None:
        cur.execute("UPDATE users SET lang=? WHERE id=?", (lang, user_id))
    conn.commit()
    conn.close()

def update_prefs(db_path: str, user_id: str,
                 tts_enabled: bool = False,
                 high_contrast: bool = False,
                 large_text: bool = False,
                 reduced_motion: bool = False,
                 captions_enabled: bool = True,
                 transcript_enabled: bool = True,
                 lang: Optional[str] = None):
    """Upsert UI/accessibility preferences for a user."""
    conn = _conn(db_path); _ensure_schema(conn)
    cur = conn.cursor()
    # Ensure user row exists
    cur.execute("INSERT OR IGNORE INTO users (id, nickname, grade, lang, created_at) "
                "VALUES (?, '', 'Other', ?, datetime('now'))",
                (user_id, lang or "en-US"))
    # Upsert prefs
    cur.execute("""
        INSERT INTO prefs (user_id, tts_enabled, high_contrast, large_text, reduced_motion,
                           captions_enabled, transcript_enabled, lang, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(user_id) DO UPDATE SET
            tts_enabled=excluded.tts_enabled,
            high_contrast=excluded.high_contrast,
            large_text=excluded.large_text,
            reduced_motion=excluded.reduced_motion,
            captions_enabled=excluded.captions_enabled,
            transcript_enabled=excluded.transcript_enabled,
            lang=excluded.lang,
            updated_at=datetime('now')
    """, (user_id,
          int(bool(tts_enabled)),
          int(bool(high_contrast)),
          int(bool(large_text)),
          int(bool(reduced_motion)),
          int(bool(captions_enabled)),
          int(bool(transcript_enabled)),
          lang or "en-US"))
    conn.commit()
    conn.close()

def get_prefs(db_path: str, user_id: str) -> Dict[str, Any]:
    """Return prefs dict; if none, returns {}."""
    conn = _conn(db_path); _ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT tts_enabled, high_contrast, large_text, reduced_motion, "
                "captions_enabled, transcript_enabled, lang "
                "FROM prefs WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {}
    return {
        "tts_enabled": bool(row[0]),
        "high_contrast": bool(row[1]),
        "large_text": bool(row[2]),
        "reduced_motion": bool(row[3]),
        "captions_enabled": bool(row[4]),
        "transcript_enabled": bool(row[5]),
        "lang": row[6] or "en-US",
    }

def get_user(db_path: str, user_id: str) -> Dict[str, Any]:
    """Fetch basic profile info from users table."""
    conn = _conn(db_path); _ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT id, nickname, grade, lang, created_at FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {}
    return {"id": row[0], "nickname": row[1], "grade": row[2], "lang": row[3], "created_at": row[4]}
