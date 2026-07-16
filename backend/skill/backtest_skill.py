


# backtest_skill

from backend.skill.model_infer_skill import Stock3DayInferSkill
from backend.db.kline_db import AShareKlineDB
from datetime import datetime

class BacktestSkill:
    def __init__(self, infer_skill: Stock3DayInferSkill, db: AShareKlineDB):
        self.infer_skill = infer_skill
        self.kline_db = db

    def run_backtest(self, start_date: str, end_date: str, stock_codes: list[str]) -> dict:
        total_positive = 0
        pred_positive = 0
        hit = 0
        signal_records = []
        for code in stock_codes:
            all_days = self.kline_db.query_date_range(code, start_date, end_date)
            for idx in range(2, len(all_days)):
                window = all_days[idx-2:idx+1]
                t_row = all_days[idx]
                t1_row = all_days[idx+1] if idx+1 < len(all_days) else None
                if not t1_row:
                    continue
                real_pct = (t1_row["close"] - t1_row["pre_close"]) / t1_row["pre_close"] * 100
                pred = self.infer_skill.run(window, code)
                is_real_big = real_pct > 1.5
                if is_real_big:
                    total_positive += 1
                if pred.is_big_rise:
                    pred_positive += 1
                    if is_real_big:
                        hit += 1
                signal_records.append({
                    "code": code,
                    "window_end": t_row["date"],
                    "pred_date": pred.target_date,
                    "pred_prob": pred.prob_up_1p5,
                    "predict_signal": pred.is_big_rise,
                    "real_gain": round(real_pct,2),
                    "real_big_rise": is_real_big
                })
        precision = hit / pred_positive if pred_positive > 0 else 0
        recall = hit / total_positive if total_positive > 0 else 0
        return {
            "signal_list": signal_records,
            "precision": round(precision,4),
            "recall": round(recall,4),
            "total_true_big_up": total_positive,
            "total_pred_signal": pred_positive,
            "hit_count": hit
        }

