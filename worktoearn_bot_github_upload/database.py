import sqlite3
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bot_database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id INTEGER PRIMARY KEY,
                ref_link TEXT NOT NULL DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Pre-seed 1 to 50 if empty
        cur = conn.execute("SELECT COUNT(*) as cnt FROM accounts")
        if cur.fetchone()["cnt"] == 0:
            for i in range(1, 51):
                conn.execute("INSERT INTO accounts (account_id, ref_link) VALUES (?, '')", (i,))
    conn.close()

def save_ref_link(account_id: int, ref_link: str):
    conn = get_db()
    with conn:
        conn.execute("""
            INSERT INTO accounts (account_id, ref_link, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(account_id) DO UPDATE SET ref_link=excluded.ref_link, updated_at=CURRENT_TIMESTAMP
        """, (account_id, ref_link.strip()))
    conn.close()

def get_ref_link(account_id: int) -> str:
    conn = get_db()
    cur = conn.execute("SELECT ref_link FROM accounts WHERE account_id = ?", (account_id,))
    row = cur.fetchone()
    conn.close()
    return row["ref_link"] if row and row["ref_link"] else ""

def get_all_accounts():
    conn = get_db()
    cur = conn.execute("SELECT account_id, ref_link FROM accounts ORDER BY account_id ASC")
    rows = cur.fetchall()
    conn.close()
    return [{"account_id": r["account_id"], "ref_link": r["ref_link"]} for r in rows]

def bulk_save_links(raw_text: str):
    """
    Parses various bulk formats:
    1. 1=https://...
    2. 1: https://...
    3. Acc 1 - https://...
    4. Just 50 links line-by-line
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    saved_count = 0
    results = []

    # Check if lines have account numbers explicitly (e.g. 1=http or 1: http or 1 - http)
    has_explicit_numbers = any(re.match(r'^(?:acc(?:ount)?\s*)?(\d{1,2})[\s:=–-]+(http[s]?://\S+)', l, re.IGNORECASE) for l in lines)

    if has_explicit_numbers:
        for line in lines:
            m = re.match(r'^(?:acc(?:ount)?\s*)?(\d{1,2})[\s:=–-]+(http[s]?://\S+)', line, re.IGNORECASE)
            if m:
                acc_id = int(m.group(1))
                link = m.group(2).strip()
                if 1 <= acc_id <= 50:
                    save_ref_link(acc_id, link)
                    saved_count += 1
                    results.append((acc_id, link))
    else:
        # Plain list of links line by line
        for idx, line in enumerate(lines, start=1):
            if idx > 50:
                break
            # Find first url in line
            url_match = re.search(r'http[s]?://\S+', line)
            if url_match:
                link = url_match.group(0).strip()
                save_ref_link(idx, link)
                saved_count += 1
                results.append((idx, link))

    return saved_count, results

# Initialize DB on load
init_db()
