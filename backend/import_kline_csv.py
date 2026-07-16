


import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

import csv
from backend.db.kline_db import AShareKlineDB
from backend.config import settings

def import_csv_to_kline(csv_file_path: str):
    db = AShareKlineDB()
    insert_sql = """
    INSERT OR IGNORE INTO kline 
    (code, date, open, high, low, close, pre_close, volume, amount)
    VALUES (?,?,?,?,?,?,?,?,?)
    """
    batch = []
    with open(csv_file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch.append((
                row["code"], row["date"],
                float(row["open"]), float(row["high"]), float(row["low"]), float(row["close"]),
                float(row["pre_close"]), int(row["volume"]), float(row["amount"])
            ))
            if len(batch) >= 10000:
                db.cur.executemany(insert_sql, batch)
                db.conn.commit()
                batch = []
    if batch:
        db.cur.executemany(insert_sql, batch)
        db.conn.commit()
    db.close()
    print("CSV data import complete")

if __name__ == "__main__":
    # Replace with your real CSV file path
    csv_path = "/home/test4ai/my_agent/stock_2020_2026.csv"
    import_csv_to_kline(csv_path)
