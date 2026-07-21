import sys
import os
import sqlite3
from datetime import datetime, timedelta

# 统一项目根路径注入
FILE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(FILE_DIR, "../"))
sys.path.insert(0, ROOT_DIR)

from backend.config import settings
from backend.config.settings import KLINE_DB_PATH, DATE_FMT

class KlineDB:
    def __init__(self):
        # 全局持久连接，放开线程校验（本地开发调试可用）
        self.db_path = settings.KLINE_DB_PATH
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cur = self.conn.cursor()

    def query_three_day_window(self, code: str, end_dt: str):
        dt_obj = datetime.strptime(end_dt, DATE_FMT)
        days = []
        current_dt = dt_obj
    
        # 向前循环查找，收集3条有效行情
        while len(days) < 3:
            date_str = current_dt.strftime(DATE_FMT)
            self.cur.execute("""
                SELECT date,open,high,low,close,pre_close,volume,amount
                FROM kline WHERE code=? AND date=?
            """, (code, date_str))
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
            # 往前推一天
            current_dt = current_dt - timedelta(days=1)
            # 防止死循环，最多往前查90天
            if (dt_obj - current_dt).days > 90:
                break
    
        valid_len = len(days)
        if valid_len != 3:
            raise ValueError(f"Kline data incomplete, expected 3 continuous trading days, got {valid_len} records")
        # 反转，按时间升序返回（最早在前）
        days = list(reversed(days))
        return days

    
    def query_date_range(self, code: str, start_date: str, end_date: str):
        sql = """
            SELECT date, open, high, low, close, pre_close, volume, amount
            FROM kline WHERE code = ? AND date BETWEEN ? AND ? ORDER BY date ASC
        """
        self.cur.execute(sql, (code, start_date, end_date))
        rows = self.cur.fetchall()
        result = []
        for r in rows:
            result.append({
                "date": r[0],
                "open": r[1],
                "high": r[2],
                "low": r[3],
                "close": r[4],
                "pre_close": r[5],
                "volume": r[6],
                "amount": r[7]
            })
        return result


    def batch_insert_kline(self, batch):
        """批量插入CSV数据，给导入脚本调用"""
        insert_sql = """
        INSERT OR IGNORE INTO kline
        (code, date, open, high, low, close, pre_close, volume, amount)
        VALUES (?,?,?,?,?,?,?,?,?)
        """
        self.cur.executemany(insert_sql, batch)
        self.conn.commit()
        print(f"批量插入完成，共 {len(batch)} 条记录")

    def get_total_count(self, stock_code: str = None):
        """校验数据库记录总数"""
        if stock_code:
            self.cur.execute("SELECT COUNT(*) FROM kline WHERE code=?", (stock_code,))
        else:
            self.cur.execute("SELECT COUNT(*) FROM kline")
        return self.cur.fetchone()[0]

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
