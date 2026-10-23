import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "proof_database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_proof_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS proofs (
                account_id INTEGER NOT NULL,
                topic_id INTEGER NOT NULL, -- 1: X Promo, 2: 20 Views Graphic, 3: Referral Graphic
                post_link TEXT DEFAULT '',
                ss_post_file_id TEXT DEFAULT '',
                ss_post_path TEXT DEFAULT '',
                ss_profile_file_id TEXT DEFAULT '',
                ss_profile_path TEXT DEFAULT '',
                ss_views_file_id TEXT DEFAULT '',
                ss_views_path TEXT DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (account_id, topic_id)
            )
        """)
        # Pre-seed 50 accounts x 3 topics if empty
        cur = conn.execute("SELECT COUNT(*) as cnt FROM proofs")
        if cur.fetchone()["cnt"] == 0:
            for acc in range(1, 51):
                for top in [1, 2, 3]:
                    conn.execute("INSERT INTO proofs (account_id, topic_id) VALUES (?, ?)", (acc, top))
    conn.close()

def save_topic_link(account_id: int, topic_id: int, post_link: str):
    conn = get_db()
    with conn:
        conn.execute("""
            INSERT INTO proofs (account_id, topic_id, post_link, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(account_id, topic_id) DO UPDATE SET post_link=excluded.post_link, updated_at=CURRENT_TIMESTAMP
        """, (account_id, topic_id, post_link.strip()))
    conn.close()

def save_topic_screenshot(account_id: int, topic_id: int, ss_type: str, file_id: str, file_path: str):
    """
    ss_type: 'post', 'profile', or 'views'
    """
    conn = get_db()
    with conn:
        if ss_type == 'post':
            conn.execute("""
                UPDATE proofs SET ss_post_file_id=?, ss_post_path=?, updated_at=CURRENT_TIMESTAMP
                WHERE account_id=? AND topic_id=?
            """, (file_id, file_path, account_id, topic_id))
        elif ss_type == 'profile':
            conn.execute("""
                UPDATE proofs SET ss_profile_file_id=?, ss_profile_path=?, updated_at=CURRENT_TIMESTAMP
                WHERE account_id=? AND topic_id=?
            """, (file_id, file_path, account_id, topic_id))
        elif ss_type == 'views':
            conn.execute("""
                UPDATE proofs SET ss_views_file_id=?, ss_views_path=?, updated_at=CURRENT_TIMESTAMP
                WHERE account_id=? AND topic_id=?
            """, (file_id, file_path, account_id, topic_id))
    conn.close()

def get_account_proofs(account_id: int):
    conn = get_db()
    cur = conn.execute("SELECT * FROM proofs WHERE account_id=? ORDER BY topic_id ASC", (account_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_proofs_summary():
    conn = get_db()
    cur = conn.execute("SELECT * FROM proofs ORDER BY account_id ASC, topic_id ASC")
    rows = cur.fetchall()
    conn.close()
    
    summary = {}
    for r in rows:
        acc = r["account_id"]
        if acc not in summary:
            summary[acc] = {1: {}, 2: {}, 3: {}}
        summary[acc][r["topic_id"]] = dict(r)
    return summary

def reset_proofs_for_account(account_id: int):
    conn = get_db()
    with conn:
        conn.execute("""
            UPDATE proofs SET post_link='', ss_post_file_id='', ss_post_path='',
                              ss_profile_file_id='', ss_profile_path='',
                              ss_views_file_id='', ss_views_path='',
                              updated_at=CURRENT_TIMESTAMP
            WHERE account_id=?
        """, (account_id,))
    conn.close()

def reset_all_proofs():
    conn = get_db()
    with conn:
        conn.execute("""
            UPDATE proofs SET post_link='', ss_post_file_id='', ss_post_path='',
                              ss_profile_file_id='', ss_profile_path='',
                              ss_views_file_id='', ss_views_path='',
                              updated_at=CURRENT_TIMESTAMP
        """)
    conn.close()

init_proof_db()
