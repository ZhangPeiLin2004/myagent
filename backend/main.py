# 路径注入放在最顶部
import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

# 全部导入
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from backend.agent.graph import stock_agent_graph
from backend.memory.session_memory import SessionMemoryManager
from backend.common.constants import TaskType

# 只创建一次 app 实例，带上版本号
app = FastAPI(title="Hermes AStock Agent API", version="0.1.0")

# 在同一个app实例上添加跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化内存管理器，只保留这一行
mem = SessionMemoryManager()

@app.post("/api/session/create")
def create_session(name: str):
    sid = mem.create_session(name)
    return {"session_id": sid}

@app.get("/api/session/list")
def list_sessions():
    records = mem.list_sessions()
    return [{"id": r.id, "name": r.name, "created_at": r.created_at} for r in records]

@app.post("/api/stock/predict")
def stock_predict(
    stock_code: str,
    window_end_date: str,
):
    init_state = {
        "task_id": "api_pred_001",
        "request_type": "single_predict",
        "stock_code": stock_code,
        "window_end_date": window_end_date,
        "backtest_start": None,
        "backtest_end": None,
        "stock_codes": None,
        "kline_window": None,
        "predict_result": None,
        "backtest_report": None,
        "step": "",
        "error_info": None,
        "finished": False
    }
    output = stock_agent_graph.invoke(init_state)
    return output

@app.post("/api/stock/backtest")
def stock_backtest(
    backtest_start: str,
    backtest_end: str,
    target_codes: list[str]
):
    init_state = {
        "task_id": "api_bt_001",
        "request_type": "backtest",
        "stock_code": None,
        "window_end_date": None,
        "backtest_start": backtest_start,
        "backtest_end": backtest_end,
        "stock_codes": target_codes,
        "kline_window": None,
        "predict_result": None,
        "backtest_report": None,
        "step": "",
        "error_info": None,
        "finished": False
    }
    output = stock_agent_graph.invoke(init_state)
    return output
