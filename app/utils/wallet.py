import os, sqlite3
from utils.paths import DB_PATH

def _conn(db_path: str = DB_PATH) -> sqlite3.Connection:
    # Make sure the directory exists (no-op for /tmp)
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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wallet (
            user_id TEXT PRIMARY KEY,
            coins INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            amount INTEGER,
            reason TEXT,
            ts TEXT,
            dedupe_key TEXT
        )
    """)
    conn.commit()

def ensure_wallet(db_path: str, user_id: str):
    conn = _conn(db_path)
    _ensure_schema(conn)
    cur = conn.cursor()
    # Use SQLite's clock to avoid Python datetime issues/redaction
    cur.execute(
        "INSERT OR IGNORE INTO wallet (user_id, coins, updated_at) VALUES (?, 0, datetime('now'))",
        (user_id,)
    )
    conn.commit()
    conn.close()

def get_balance(db_path: str, user_id: str) -> int:
    conn = _conn(db_path); _ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT coins FROM wallet WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return int(row[0]) if row else 0

def add_coins(db_path: str, user_id: str, amount: int, reason: str, dedupe_key: str | None = None) -> bool:
    """
    Idempotent add: if dedupe_key provided and already present, returns False.
    Returns True only when a new grant is recorded.
    """
    conn = _conn(db_path); _ensure_schema(conn)
    cur = conn.cursor()
    if dedupe_key:
        cur.execute("SELECT 1 FROM transactions WHERE user_id=? AND dedupe_key=?", (user_id, dedupe_key))
        if cur.fetchone():
            conn.close()
            return False
    cur.execute("UPDATE wallet SET coins = COALESCE(coins,0) + ?, updated_at = datetime('now') WHERE user_id=?", (amount, user_id))
    if cur.rowcount == 0:
        # If wallet row somehow missing, create then update
        cur.execute("INSERT OR IGNORE INTO wallet (user_id, coins, updated_at) VALUES (?, 0, datetime('now'))", (user_id,))
        cur.execute("UPDATE wallet SET coins = COALESCE(coins,0) + ?, updated_at = datetime('now') WHERE user_id=?", (amount, user_id))
    cur.execute(
        "INSERT INTO transactions (user_id, amount, reason, ts, dedupe_key) VALUES (?, ?, ?, datetime('now'), ?)",
        (user_id, amount, reason, dedupe_key)
    )
    conn.commit()
    conn.close()
    return True

def recent_transactions(db_path: str, user_id: str, limit: int = 5):
    conn = _conn(db_path); _ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(
        "SELECT amount, reason, ts FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cur.fetchall()
    conn.close()
    return rows
