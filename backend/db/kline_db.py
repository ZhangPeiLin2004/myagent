


# backend/db/kline_db.py
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

import sqlite3
from datetime import datetime, timedelta
from backend.common.constants import DATE_FMT
from backend.config import settings

class AShareKlineDB:
    def __init__(self):
        self.conn = sqlite3.connect(settings.KLINE_DB_PATH, check_same_thread=False)
        self.cur = self.conn.cursor()

    def query_three_day_window(self, code: str, end_dt: str):
        dt_obj = datetime.strptime(end_dt, DATE_FMT)
        days = []
        for offset in [2,1,0]:
            q_dt = (dt_obj - timedelta(days=offset)).strftime(DATE_FMT)
            self.cur.execute("""
                SELECT date,open,high,low,close,pre_close,volume,amount
                FROM kline WHERE code=? AND date=?
            """, (code, q_dt))
            row = self.cur.fetchone()
            if row:
                days.append({
                    "date": row[0],
                    "open": row[1],
                    "high": row[2],
                    "low": row[3],
                    "close": row[4],
                    "pre_close": row[5],
                    "volume": row[6],
                    "amount": row[7]
                })
        return days

    def query_date_range(self, code: str, start: str, end: str):
        self.cur.execute("""
            SELECT date,open,high,low,close,pre_close,volume,amount
            FROM kline WHERE code=? AND date BETWEEN ? AND ? ORDER BY date ASC
        """, (code, start, end))
        res = []
        for r in self.cur.fetchall():
            res.append({
                "date": r[0],
                "open": r[1],
                "high": r[2],
                "low": r[3],
                "close": r[4],
                "pre_close": r[5],
                "volume": r[6],
                "amount": r[7]
            })
        return res

    def close(self):
        self.conn.close()

def init_kline_database():
    db_path = settings.KLINE_DB_PATH
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    print(f"Try to create kline DB at absolute path: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS kline (
        code TEXT NOT NULL,
        date TEXT NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        pre_close REAL,
        volume INTEGER,
        amount REAL,
        PRIMARY KEY (code, date)
    )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_code_date ON kline(code, date);")
    conn.commit()
    conn.close()
    print(f"✅ A-share kline DB initialized: {db_path}")

if __name__ == "__main__":
    init_kline_database()
