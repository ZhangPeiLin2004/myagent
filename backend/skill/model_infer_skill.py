


# model_infer_skill

import joblib
import numpy as np
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class PredictResult:
    stock_code: str
    target_date: str
    prob_up_1p5: float
    threshold: float
    is_big_rise: bool

class Stock3DayInferSkill:
    def __init__(self, model_path: str, scaler_path: str, threshold: float):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.threshold = threshold

    def calc_single_kline_feature(self, row: dict) -> list[float]:
        pc = row["pre_close"]
        close = row["close"]
        open_p = row["open"]
        high = row["high"]
        low = row["low"]
        vol = row["volume"]
        amt = row["amount"]

        f1 = (close - pc) / pc
        f2 = (open_p - pc) / pc
        f3 = (high - pc) / pc
        f4 = (low - pc) / pc
        f5 = (high - low) / pc
        f6 = vol / 1000000
        f7 = amt / 100000000
        f8 = close / open_p if open_p != 0 else 1.0
        f9 = high / close if close != 0 else 1.0
        f10 = low / close if close != 0 else 1.0
        f11 = (close - (pc*5+close)/5) / pc
        f12 = (close - (pc*20+close)/20) / pc
        return [f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12]

    def run(self, window_kline: list[dict], stock_code: str) -> PredictResult:
        feat_list = []
        for kline in window_kline:
            feat_list.extend(self.calc_single_kline_feature(kline))
        X = np.array([feat_list])
        X_scaled = self.scaler.transform(X)
        prob = self.model.predict_proba(X_scaled)[0, 1]
        end_date = window_kline[-1]["date"]
        target_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        target_date = target_dt.strftime("%Y-%m-%d")
        is_big_rise = prob > self.threshold
        return PredictResult(
            stock_code=stock_code,
            target_date=target_date,
            prob_up_1p5=round(float(prob),4),
            threshold=self.threshold,
            is_big_rise=is_big_rise
        )

