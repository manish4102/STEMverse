
import sqlite3, datetime, uuid

def conn(db_path): 
    return sqlite3.connect(db_path)

def ensure_user(db_path, user_id, nickname="", grade="", lang="en"):
    c = conn(db_path); cur = c.cursor()
    cur.execute("INSERT OR IGNORE INTO users (id, nickname, grade, lang, created_at) VALUES (?,?,?,?,?)",
                (user_id, nickname, grade, lang, datetime.datetime.utcnow().isoformat()))
    c.commit(); c.close()

def update_prefs(db_path, user_id, **prefs):
    c = conn(db_path); cur = c.cursor()
    keys = ["tts_enabled","high_contrast","large_text","reduced_motion","captions_enabled","transcript_enabled","lang"]
    for k,v in prefs.items():
        if k in keys:
            cur.execute(f"UPDATE users SET {k}=? WHERE id=?", (int(v) if isinstance(v,bool) else v, user_id))
    c.commit(); c.close()

def get_user(db_path, user_id):
    c = conn(db_path); cur=c.cursor()
    cur.execute("SELECT id, nickname, grade, lang, tts_enabled, high_contrast, large_text, reduced_motion, captions_enabled, transcript_enabled FROM users WHERE id=?", (user_id,))
    row = cur.fetchone(); c.close()
    if not row: return None
    keys = ["id","nickname","grade","lang","tts_enabled","high_contrast","large_text","reduced_motion","captions_enabled","transcript_enabled"]
    return dict(zip(keys,row))
