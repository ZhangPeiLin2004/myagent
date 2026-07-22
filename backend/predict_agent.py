import sys
import os
import pandas as pd
import numpy as np
import xgboost as xgb

# 路径注入
CUR_FILE = os.path.abspath(__file__)
BACKEND_DIR = os.path.dirname(CUR_FILE)
ROOT_DIR = os.path.dirname(BACKEND_DIR)
sys.path.insert(0, ROOT_DIR)

from backend.tools.data_query_tool import DataQueryTool
from backend.db.kline_db import KlineDB

# 三个分位数模型文件
MODEL_MEDIAN = os.path.join(BACKEND_DIR, "stock_quant_0.5.xgb")
MODEL_LOW = os.path.join(BACKEND_DIR, "stock_quant_0.05.xgb")
MODEL_HIGH = os.path.join(BACKEND_DIR, "stock_quant_0.95.xgb")

class StockPredictAgent:
    def __init__(self):
        self.query_tool = DataQueryTool()
        self.kline_db = KlineDB()
        self.model_median = None
        self.model_low = None
        self.model_high = None
        self.load_all_models()

    def load_all_models(self):
        """加载三组分位数模型"""
        if os.path.exists(MODEL_MEDIAN):
            self.model_median = xgb.Booster()
            self.model_median.load_model(MODEL_MEDIAN)
        if os.path.exists(MODEL_LOW):
            self.model_low = xgb.Booster()
            self.model_low.load_model(MODEL_LOW)
        if os.path.exists(MODEL_HIGH):
            self.model_high = xgb.Booster()
            self.model_high.load_model(MODEL_HIGH)

    def build_features_from_df(self, df):
        df = df.copy()
        df["return"] = (df["close"] - df["pre_close"]) / df["pre_close"]
        df["ma3"] = df["close"].rolling(3).mean()
        df["vol_ma3"] = df["volume"].rolling(3).mean()
        df["amplitude"] = df["high"] - df["low"]

        # 标签：下一日涨跌幅（连续值）
        df["target_pct"] = df["return"].shift(-1)
        df = df.dropna()
        feature_cols = ["return", "ma3", "vol_ma3", "amplitude"]
        X = df[feature_cols]
        y = df["target_pct"]
        return X, y, df

    def train_quantile_model(self, X_train, y_train, tau, save_path):
        """训练单个分位数模型"""
        dtrain = xgb.DMatrix(X_train, label=y_train)
        params = {
            "objective": "reg:quantileerror",
            "quantile_alpha": tau,
            "eval_metric": "quantile",
            "verbosity": 0
        }
        model = xgb.train(params, dtrain, num_boost_round=120)
        model.save_model(save_path)
        return model

    def train_model(self, stock_code="000001"):
        all_data = self.kline_db.query_date_range(stock_code, start_date="2024-01-01", end_date="2026-07-20")
        if len(all_data) < 30:
            return {"success": False, "msg": "历史K线样本不足30条，无法训练"}
        df = pd.DataFrame(all_data)
        X, y, _ = self.build_features_from_df(df)
        split_idx = int(len(X)*0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        # 训练三组分位数
        self.model_low = self.train_quantile_model(X_train, y_train, 0.05, MODEL_LOW)
        self.model_median = self.train_quantile_model(X_train, y_train, 0.5, MODEL_MEDIAN)
        self.model_high = self.train_quantile_model(X_train, y_train, 0.95, MODEL_HIGH)

        return {
            "success": True,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "msg": "XGBoost分位数回归训练完成，输出涨跌幅预测+90%置信区间"
        }

    def predict_next_day(self, stock_code: str):
        data_res = self.query_tool.get_recent_3_trade_data(stock_code)
        if not data_res["success"]:
            return {
                "stock_code": stock_code,
                "warning": data_res["msg"],
                "raw_3day_data": data_res["data"]
            }
        raw_data = data_res["data"]
        if not all([self.model_low, self.model_median, self.model_high]):
            return {
                "stock_code": stock_code,
                "warning": "模型尚未训练，请调用 /api/stock/train",
                "raw_3day_data": raw_data
            }

        # 构造推理特征
        df = pd.DataFrame(raw_data)
        df["return"] = (df["close"] - df["pre_close"]) / df["pre_close"]
        df["ma3"] = df["close"].mean()
        df["vol_ma3"] = df["volume"].mean()
        df["amplitude"] = df["high"].max() - df["low"].min()
        feat_infer = df[["return","ma3","vol_ma3","amplitude"]].iloc[-1:]
        dmat = xgb.DMatrix(feat_infer)

        # 预测三组分位数（涨跌幅，小数形式）
        pred_p5 = float(self.model_low.predict(dmat)[0])
        pred_med = float(self.model_median.predict(dmat)[0])
        pred_p95 = float(self.model_high.predict(dmat)[0])

        # 根据中位数幅度判断涨跌方向
        predict_result = "up" if pred_med > 0 else "down"

        return {
            "stock_code": stock_code,
            "predict_result": predict_result,
            "pred_pct_median": round(pred_med * 100, 2),    # 中位数涨跌幅 %
            "pred_pct_low": round(pred_p5 * 100, 2),        # 5%分位下限 %
            "pred_pct_high": round(pred_p95 * 100, 2),      # 95%分位上限 %
            "confidence": "90%",
            "raw_3day_data": raw_data
        }

    def close(self):
        self.query_tool.close()

if __name__ == "__main__":
    agent = StockPredictAgent()
    # agent.train_model("000001")
    res = agent.predict_next_day("000001")
    print(res)
