import sys
import os

# 获取当前脚本路径
CUR_FILE = os.path.abspath(__file__)
# tools目录
TOOLS_DIR = os.path.dirname(CUR_FILE)
# 向上一层拿到 backend
BACKEND_DIR = os.path.dirname(TOOLS_DIR)
# 再向上拿到项目根目录 my_agent
ROOT_DIR = os.path.dirname(BACKEND_DIR)
# 插入根目录到sys.path
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.db.kline_db import KlineDB

class DataQueryTool:
    def __init__(self):
        self.kline_db = KlineDB()

    def get_recent_3_trade_data(self, stock_code: str):
        """获取股票最近3个交易日行情，供预测模型使用"""
        try:
            data = self.kline_db.query_three_day_window(stock_code, "2026-07-20")
            return {
                "code": stock_code,
                "data": data,
                "success": True
            }
        except Exception as e:
            return {
                "success": False,
                "msg": str(e)
            }

    def get_stock_range_data(self, stock_code: str, start: str, end: str):
        data = self.kline_db.query_date_range(stock_code, start, end)
        return {"code": stock_code, "list": data}

    def close(self):
        self.kline_db.close()

if __name__ == "__main__":
    tool = DataQueryTool()
    res = tool.get_recent_3_trade_data("000001")
    print("工具查询结果：")
    print(res)
    tool.close()
