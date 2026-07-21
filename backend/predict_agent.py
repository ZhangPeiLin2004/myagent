import sys
import os

# 路径注入
CUR_FILE = os.path.abspath(__file__)
BACKEND_DIR = os.path.dirname(CUR_FILE)
ROOT_DIR = os.path.dirname(BACKEND_DIR)
sys.path.insert(0, ROOT_DIR)

import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from backend.tools.data_query_tool import DataQueryTool
from backend.db.kline_db import KlineDB

MODEL_PATH = os.path.join(BACKEND_DIR, "stock_model.lgb")

class StockPredictAgent:
    def __init__(self):
        self.query_tool = DataQueryTool()
        self.kline_db = KlineDB()
        self.model = None
        self.load_model()

    def load_model(self):
        """加载本地训练好的模型文件"""
        if os.path.exists(MODEL_PATH):
            self.model = lgb.Booster(model_file=MODEL_PATH)

    def build_features_from_df(self, df):
        """从全量历史K线构造训练特征 + 标签"""
        df = df.copy()
        df["return"] = (df["close"] - df["pre_close"]) / df["pre_close"]
        df["ma3"] = df["close"].rolling(3).mean()
        df["vol_ma3"] = df["volume"].rolling(3).mean()
        df["amplitude"] = df["high"] - df["low"]
        # 标签：下一个交易日是否上涨（1=上涨，0=下跌）
        df["target"] = (df["return"].shift(-1) > 0).astype(int)
        df = df.dropna()
        feature_cols = ["return", "ma3", "vol_ma3", "amplitude"]
        X = df[feature_cols]
        y = df["target"]
        return X, y, df

    def train_model(self, stock_code="000001"):
        """训练LightGBM二分类模型"""
        all_data = self.kline_db.query_date_range(stock_code, start_date="2024-01-01", end_date="2026-07-20")
        if len(all_data) < 20:
            return {"success": False, "msg": "历史K线样本不足20条，无法训练模型"}
        df = pd.DataFrame(all_data)
        X, y, _ = self.build_features_from_df(df)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

        params = {
            "objective": "binary",
            "metric": "binary_logloss",
            "verbose": -1
        }
        lgb_train = lgb.Dataset(X_train, label=y_train)
        lgb_eval = lgb.Dataset(X_test, label=y_test, reference=lgb_train)
        self.model = lgb.train(params, lgb_train, valid_sets=[lgb_eval], num_boost_round=100)
        # 持久化模型
        self.model.save_model(MODEL_PATH)
        # 评估准确率
        y_pred = self.model.predict(X_test)
        y_pred_bin = (y_pred > 0.5).astype(int)
        acc = accuracy_score(y_test, y_pred_bin)
        return {
            "success": True,
            "accuracy": round(float(acc), 4),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "msg": "模型训练完成，已保存至本地"
        }

    def build_feature(self, data_list):
        """构造推理输入特征（保持原有函数，兼容旧逻辑）"""
        df = pd.DataFrame(data_list)
        feat = {}
        feat["mean_close"] = df["close"].mean()
        feat["mean_volume"] = df["volume"].mean()
        feat["price_range"] = df["high"].max() - df["low"].min()
        last_close = df.iloc[-1]["close"]
        last_pre = df.iloc[-1]["pre_close"]
        feat["last_pct"] = (last_close - last_pre) / last_pre
        return feat

    def predict_next_day(self, stock_code: str):
        """模型推理预测，优先使用训练好的LightGBM；未训练时提示"""
        data_res = self.query_tool.get_recent_3_trade_data(stock_code)
        if not data_res["success"]:
            return {
                "stock_code": stock_code,
                "predict_result": None,
                "warning": data_res["msg"],
                "raw_3day_data": data_res["data"]
            }
        data = data_res["data"]
        if self.model is None:
            return {
                "stock_code": stock_code,
                "predict_result": None,
                "warning": "模型尚未训练，请先调用训练接口 /api/stock/train",
                "raw_3day_data": data
            }
        # 构造推理特征
        feat_df = pd.DataFrame(data)
        feat_df["return"] = (feat_df["close"] - feat_df["pre_close"]) / feat_df["pre_close"]
        feat_df["ma3"] = feat_df["close"].mean()
        feat_df["vol_ma3"] = feat_df["volume"].mean()
        feat_df["amplitude"] = feat_df["high"].max() - feat_df["low"].min()
        feat_infer = feat_df[["return","ma3","vol_ma3","amplitude"]].iloc[-1:]
        prob = self.model.predict(feat_infer)[0]
        pred_result = "up" if prob > 0.5 else "down"
        return {
            "stock_code": stock_code,
            "predict_prob": round(float(prob),4),
            "predict_result": pred_result,
            "raw_3day_data": data
        }

    def close(self):
        self.query_tool.close()

if __name__ == "__main__":
    agent = StockPredictAgent()
    # agent.train_model("000001")
    res = agent.predict_next_day("000001")
    print("Agent预测结果：")
    print(res)
    agent.close()
