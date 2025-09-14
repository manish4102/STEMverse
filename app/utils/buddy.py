
import sqlite3, uuid, datetime

def _conn(db_path): return sqlite3.connect(db_path)

def create_or_join_room(db_path, code):
    conn = _conn(db_path); cur = conn.cursor()
    # Try find or create
    cur.execute("SELECT id FROM rooms WHERE code=?",(code,))
    row = cur.fetchone()
    if row is None:
        rid = str(uuid.uuid4())
        cur.execute("INSERT INTO rooms (id, code, status) VALUES (?,?,?)",(rid, code, "open"))
        conn.commit()
    else:
        rid = row[0]
    conn.close()
    return rid

def add_member(db_path, room_id, user_id, role):
    conn=_conn(db_path); cur=conn.cursor()
    cur.execute("INSERT INTO room_members (id, room_id, user_id, role) VALUES (?,?,?,?)",
                (str(uuid.uuid4()), room_id, user_id, role))
    conn.commit(); conn.close()

def list_members(db_path, room_id):
    conn=_conn(db_path); cur=conn.cursor()
    cur.execute("SELECT user_id, role FROM room_members WHERE room_id=?",(room_id,))
    m = cur.fetchall(); conn.close(); return m

def post_message(db_path, room_id, user_id, text):
    conn=_conn(db_path); cur=conn.cursor()
    cur.execute("INSERT INTO messages (id, room_id, user_id, text, ts) VALUES (?,?,?,?,?)",
                (str(uuid.uuid4()), room_id, user_id, text, datetime.datetime.utcnow().isoformat()))
    conn.commit(); conn.close()

def get_messages(db_path, room_id, since_iso=None):
    conn=_conn(db_path); cur=conn.cursor()
    if since_iso:
        cur.execute("SELECT user_id, text, ts FROM messages WHERE room_id=? AND ts>? ORDER BY ts ASC",(room_id, since_iso))
    else:
        cur.execute("SELECT user_id, text, ts FROM messages WHERE room_id=? ORDER BY ts ASC",(room_id,))
    rows = cur.fetchall(); conn.close(); return rows
