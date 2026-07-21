import sys
import os
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(FILE_DIR, "../")
sys.path.insert(0, ROOT_DIR)

from backend.config import settings
from backend.db.kline_db import KlineDB

print(f"Kline DB Path: {settings.KLINE_DB_PATH}")
db = KlineDB()

# 纯数字代码 + 导出截止日期
res = db.query_three_day_window("000001", "2026-07-20")
print(f"Query result length: {len(res)}")
print(res)

# 额外校验总条数
count = db.get_total_count("000001")
print(f"单只股票总记录：{count}")
db.close()
