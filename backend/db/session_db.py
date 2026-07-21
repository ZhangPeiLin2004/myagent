import sqlite3
from backend.config.settings import AGENT_DB_PATH

def init_session_database():
    conn = sqlite3.connect(AGENT_DB_PATH)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        created_at TEXT
    )
    ''')
    conn.commit()
    conn.close()
    print(f"Try to create session DB at absolute path: {AGENT_DB_PATH}")
    print(f"✅ Session DB initialized successfully: {AGENT_DB_PATH}")
