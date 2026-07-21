import sys
import os
# 将项目根目录加入Python搜索路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.insert(0, ROOT_DIR)

from backend.db.session_db import init_session_database
from backend.db.kline_db import init_kline_database

if __name__ == "__main__":
    print("=== Initialize Session Database ===")
    init_session_database()
    print("\n=== Initialize A-share Kline Database ===")
    init_kline_database()
    print("\nAll databases & tables created successfully!")
