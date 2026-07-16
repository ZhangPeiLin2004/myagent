


# main

import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

# 下面原有所有导入不动
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import json
from backend.agent.graph import stock_agent_graph
from backend.memory.session_memory import SessionMemoryManager
from backend.common.constants import TaskType

app = FastAPI(title="Hermes AStock Agent API")
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
