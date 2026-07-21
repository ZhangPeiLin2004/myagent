import os

# 当前配置文件目录
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# 项目根目录 my_agent/
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../"))
# 数据库文件统一存放根目录 my_agent/db/
DB_ROOT = os.path.join(ROOT_DIR, "db")

# 会话数据库路径
AGENT_DB_PATH = os.path.join(DB_ROOT, "agent.db")
# A股行情数据库路径
KLINE_DB_PATH = os.path.join(DB_ROOT, "ashare_kline.db")

# 模型文件目录
MODEL_DIR = os.path.join(ROOT_DIR, "backend/model")
LGB_MODEL_PATH = os.path.join(MODEL_DIR, "lgb_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

# 日期格式常量
DATE_FMT = "%Y-%m-%d"
