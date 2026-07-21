import sys
import os

# 强制注入项目根目录，解决 ModuleNotFoundError
current_file = os.path.abspath(__file__)
backend_dir = os.path.dirname(current_file)
root_dir = os.path.dirname(backend_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.predict_agent import StockPredictAgent

app = FastAPI(title="Stock Agent Backend Service")

# 跨域配置，前端访问必备
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = StockPredictAgent()

# 新增训练接口（放在其他路由同级位置）
@app.post("/api/stock/train")
def train_stock_model(code: str = "000001"):
    return agent.train_model(code)


@app.get("/")
def index():
    return {
        "service": "Stock Agent Backend",
        "docs": "http://127.0.0.1:8000/docs"
    }

# 三日K线接口
@app.get("/api/kline/three")
def get_three_kline(code: str = "000001"):
    return agent.query_tool.get_recent_3_trade_data(code)

# 预测接口
@app.get("/api/predict")
def stock_predict(code: str = "000001"):
    return agent.predict_next_day(code)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
