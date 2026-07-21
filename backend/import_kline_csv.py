import sys
import os
import csv

FILE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(FILE_DIR, "../"))
sys.path.insert(0, ROOT_DIR)

from backend.config.settings import KLINE_DB_PATH
from backend.db.kline_db import KlineDB

# CSV文件路径
CSV_SAVE_PATH = os.path.join(ROOT_DIR, "data/kline_csv/stock_2020_2026.csv")

def import_csv_to_kline():
    # 实例化全局KlineDB
    db = KlineDB()

    # 读取CSV批量组装数据
    batch_data = []
    with open(CSV_SAVE_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch_data.append((
                row["code"],
                row["date"],
                float(row["open"]),
                float(row["high"]),
                float(row["low"]),
                float(row["close"]),
                float(row["pre_close"]),
                int(row["volume"]),
                float(row["amount"])
            ))

    # 调用类内置批量插入方法
    db.batch_insert_kline(batch_data)

    # 校验导入条数
    total = db.get_total_count("000001")
    print(f"股票000001总行情条数：{total}")

    db.close()

if __name__ == "__main__":
    import_csv_to_kline()
