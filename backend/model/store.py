


# backend/model/store.py 顶部增加路径处理
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

import joblib
import yaml
from backend.skill.model_infer_skill import Stock3DayInferSkill
from backend.db.kline_db import AShareKlineDB

class ModelStoreModule:
    def __init__(self, model_path: str, scaler_path: str):
        self.model_path = os.path.abspath(os.path.join(project_root, model_path))
        self.scaler_path = os.path.abspath(os.path.join(project_root, scaler_path))
        self.cfg = self._load_config()
        self.kline_db = AShareKlineDB()

    def _load_config(self):
        # 绝对路径指向项目根目录config/model_config.yaml
        yaml_path = os.path.join(project_root, "config", "model_config.yaml")
        with open(yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def load_model(self):
        return joblib.load(self.model_path)

    def load_scaler(self):
        return joblib.load(self.scaler_path)

    def get_opt_threshold(self) -> float:
        return self.cfg["stock_predict"]["model_prob_threshold"]

    def build_infer_skill(self):
        return Stock3DayInferSkill(
            model_path=self.model_path,
            scaler_path=self.scaler_path,
            threshold=self.get_opt_threshold()
        )
