
import sqlite3, uuid, datetime

def _conn(db_path): return sqlite3.connect(db_path)

def ensure_wallet(db_path, user_id):
    conn=_conn(db_path); cur=conn.cursor()
    cur.execute("INSERT OR IGNORE INTO wallet (user_id, coins, updated_at) VALUES (?,?,?)",
                (user_id, 0, datetime.datetime.utcnow().isoformat()))
    conn.commit(); conn.close()

def get_balance(db_path, user_id):
    conn=_conn(db_path); cur=conn.cursor()
    cur.execute("SELECT coins FROM wallet WHERE user_id=?",(user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def recent_transactions(db_path, user_id, limit=10):
    conn=_conn(db_path); cur=conn.cursor()
    cur.execute("SELECT amount, reason, ts FROM transactions WHERE user_id=? ORDER BY ts DESC LIMIT ?",
                (user_id, limit))
    rows = cur.fetchall(); conn.close()
    return rows

def add_coins(db_path, user_id, amount, reason, dedupe_key=None):
    conn=_conn(db_path); cur=conn.cursor()
    if dedupe_key:
        cur.execute("SELECT 1 FROM transactions WHERE user_id=? AND dedupe_key=?",(user_id, dedupe_key))
        if cur.fetchone(): # already granted
            conn.close(); return False
    cur.execute("UPDATE wallet SET coins = COALESCE(coins,0)+?, updated_at=? WHERE user_id=?",
                (amount, datetime.datetime.utcnow().isoformat(), user_id))
    cur.execute("INSERT INTO transactions (id, user_id, amount, reason, dedupe_key, ts) VALUES (?,?,?,?,?,?)",
                (str(uuid.uuid4()), user_id, amount, reason, dedupe_key, datetime.datetime.utcnow().isoformat()))
    conn.commit(); conn.close()
    return True
