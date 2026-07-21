import sys
import os
import baostock as bs
import pandas as pd

# 注入项目根路径
FILE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(FILE_DIR, "../"))
sys.path.insert(0, ROOT_DIR)

# CSV输出路径
CSV_DIR = os.path.join(ROOT_DIR, "data/kline_csv")
CSV_SAVE_PATH = os.path.join(CSV_DIR, "stock_2020_2026.csv")

# 导出区间
START_DATE = "2020-01-01"
END_DATE = "2026-07-20"
# 单只目标股票（平安银行 sz.000001）
TARGET_STOCK = "sz.000001"

def get_stock_daily_data(stock_code: str, start_date: str, end_date: str, adjustflag: str = "3") -> pd.DataFrame:
    lg = bs.login()
    if lg.error_code != "0":
        print(f"登录失败：{lg.error_msg}")
        return pd.DataFrame()

    rs = bs.query_history_k_data_plus(
        code=stock_code,
        fields="date,open,high,low,close,preclose,volume,amount,turn,pctChg",
        start_date=start_date,
        end_date=end_date,
        frequency="d",
        adjustflag=adjustflag
    )

    data_list = []
    while (rs.error_code == "0") & rs.next():
        data_list.append(rs.get_row_data())

    columns = ["date", "open", "high", "low", "close", "pre_close", "volume", "amount", "turn", "pctChg"]
    df = pd.DataFrame(data_list, columns=columns)

    num_cols = ["open", "high", "low", "close", "pre_close", "volume", "amount", "turn", "pctChg"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col])

    df = df.sort_values("date").reset_index(drop=True)
    bs.logout()
    return df

def export_single_stock_csv():
    # 强制创建目录，不存在就新建
    if not os.path.exists(CSV_DIR):
        os.makedirs(CSV_DIR)
        print(f"自动创建目录：{CSV_DIR}")

    print(f"=== Start export stock: {TARGET_STOCK} ===")
    df = get_stock_daily_data(TARGET_STOCK, START_DATE, END_DATE, adjustflag="3")
    if df.empty:
        print("Error: No kline data fetched!")
        return
    # 纯数字股票代码
    df["code"] = TARGET_STOCK.split(".")[-1]
    save_df = df[["code", "date", "open", "high", "low", "close", "pre_close", "volume", "amount"]].copy()
    # 改用原生open写入，绕开pandas目录校验bug
    with open(CSV_SAVE_PATH, "w", encoding="utf-8", newline="") as f:
        save_df.to_csv(f, index=False)
    print(f"Export finished! File: {CSV_SAVE_PATH}, total rows: {len(save_df)}")

if __name__ == "__main__":
    export_single_stock_csv()
