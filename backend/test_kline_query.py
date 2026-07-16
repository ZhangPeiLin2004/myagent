


import sys
import os
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root)

from backend.db.kline_db import AShareKlineDB
from backend.config import settings

if __name__ == "__main__":
    print("Kline DB Path:", settings.KLINE_DB_PATH)
    db = AShareKlineDB()
    res = db.query_three_day_window("000001.SZ", "2026-07-03")
    print("Query result length:", len(res))
    db.close()
