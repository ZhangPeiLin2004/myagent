import sys
import os
import akshare as ak
import pandas as pd

# 注入项目根路径
FILE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(FILE_DIR, "../"))
sys.path.insert(0, ROOT_DIR)

# 输出CSV完整路径
CSV_SAVE_PATH = os.path.join(ROOT_DIR, "data/kline_csv/stock_2020_2026.csv")
# 导出时间区间
START_DATE = "20200101"
END_DATE = "20260720"

def export_all_ashare_daily():
    # 1. 获取全A股股票代码列表
    stock_df = ak.stock_info_a_code_name()
    stock_code_list = stock_df["code"].tolist()
    print(f"共获取A股个股总数：{len(stock_code_list)}")

    # 存储全市场行情
    all_kline_data = []

    for idx, code in enumerate(stock_code_list):
        print(f"正在导出 {idx+1}/{len(stock_code_list)} 股票代码: {code}")
        try:
            # 拉取个股日线数据
            df = ak.stock_zh_a_daily(symbol=code, start_date=START_DATE, end_date=END_DATE, adjust="")
            if df.empty:
                print(f"股票 {code} 无行情数据，跳过")
                continue
            # 中文列名映射英文标准字段
            df["code"] = code
            df = df.rename(columns={
                "date": "date",
                "开盘": "open",
                "最高": "high",
                "最低": "low",
                "收盘": "close",
                "前收盘": "pre_close",
                "成交量": "volume",
                "成交额": "amount"
            })
            # 筛选标准字段顺序
            df_out = df[["code", "date", "open", "high", "low", "close", "pre_close", "volume", "amount"]].copy()
            # 统一日期格式
            df_out["date"] = pd.to_datetime(df_out["date"]).dt.strftime("%Y-%m-%d")
            all_kline_data.append(df_out)
        except Exception as e:
            print(f"股票 {code} 导出异常，跳过，错误信息：{str(e)}")
            continue

    # 合并全部股票数据，写入CSV
    if all_kline_data:
        total_df = pd.concat(all_kline_data, axis=0, ignore_index=True)
        total_df.to_csv(CSV_SAVE_PATH, index=False, encoding="utf-8")
        print(f"\n=== 导出完成 ===")
        print(f"CSV文件路径：{CSV_SAVE_PATH}")
        print(f"总行情记录条数：{len(total_df)}")
    else:
        print("未获取到任何行情数据，CSV未生成")

if __name__ == "__main__":
    export_all_ashare_daily()
