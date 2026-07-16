


# backend/agent/graph.py
from typing import TypedDict, Optional, Dict, Any, Literal
from langgraph.graph import StateGraph, END
from dataclasses import asdict
from backend.common.msg_bus import MessageBus, AgentMessage
from backend.agent.sub.stock_predict_agent import StockPredictSubAgent
from backend.tools.data_query_tool import DataQueryTool
from backend.skill.model_infer_skill import Stock3DayInferSkill, PredictResult
from backend.skill.backtest_skill import BacktestSkill

# Global message bus
bus = MessageBus()
data_tool = DataQueryTool()

# ========= Dummy fake skill to skip missing pkl model =========
class DummyInferSkill:
    def __init__(self):
        self.threshold = 0.62

    def run(self, window_kline: list[dict], stock_code: str) -> PredictResult:
        from datetime import datetime, timedelta
        end_date = window_kline[-1]["date"]
        t1 = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        return PredictResult(
            stock_code=stock_code,
            target_date=t1.strftime("%Y-%m-%d"),
            prob_up_1p5=0.0,
            threshold=self.threshold,
            is_big_rise=False
        )

class DummyBacktestSkill:
    def __init__(self, infer):
        self.infer = infer
    def run_backtest(self, start_date, end_date, stock_codes):
        return {
            "signal_list": [],
            "precision": 0,
            "recall": 0,
            "total_true_big_up": 0,
            "total_pred_signal": 0,
            "hit_count": 0
        }

# Replace real model skill with dummy
infer_skill = DummyInferSkill()
backtest_skill = DummyBacktestSkill(infer_skill)

# Init sub agent without model file dependency
stock_sub_agent = StockPredictSubAgent(
    agent_id="stock_predict_sub_01",
    bus=bus,
    data_tool=data_tool,
    infer_skill=infer_skill,
    backtest_skill=backtest_skill
)

# ================= The rest of graph.py remains unchanged =================
class GlobalAgentState(TypedDict):
    task_id: str
    request_type: Literal["single_predict", "backtest", None]
    stock_code: Optional[str]
    window_end_date: Optional[str]
    backtest_start: Optional[str]
    backtest_end: Optional[str]
    stock_codes: Optional[list[str]]
    kline_window: Optional[list[Dict[str, Any]]]
    predict_result: Optional[Dict[str, Any]]
    backtest_report: Optional[Dict[str, Any]]
    step: str
    error_info: Optional[str]
    finished: bool

def orchestrator_node(state: GlobalAgentState) -> GlobalAgentState:
    req_type = state["request_type"]
    if req_type == "single_predict":
        state["step"] = "fetch_kline"
    elif req_type == "backtest":
        state["step"] = "run_backtest"
    else:
        state["error_info"] = "不支持的任务类型"
        state["step"] = "finish"
        state["finished"] = True
    return state

def fetch_kline_node(state: GlobalAgentState) -> GlobalAgentState:
    code = state["stock_code"]
    end_dt = state["window_end_date"]
    task_id = state["task_id"]
    tool_resp = data_tool.execute(call_id=task_id, stock_code=code, end_date=end_dt)
    if not tool_resp["success"]:
        state["error_info"] = tool_resp["error_msg"]
        state["step"] = "finish"
        state["finished"] = True
        return state
    state["kline_window"] = tool_resp["data"]
    state["step"] = "stock_sub_infer"
    return state

def stock_sub_infer_node(state: GlobalAgentState) -> GlobalAgentState:
    kline = state["kline_window"]
    code = state["stock_code"]
    # Add null & empty check
    if not kline or len(kline) != 3:
        state["error_info"] = f"Kline data incomplete, got {len(kline) if kline else 0} records, need exactly 3 days"
        state["step"] = "aggregate_result"
        state["predict_result"] = None
        return state
    res = stock_sub_agent.infer_skill.run(kline, code)
    state["predict_result"] = asdict(res)
    state["step"] = "aggregate_result"
    return state


def run_backtest_node(state: GlobalAgentState) -> GlobalAgentState:
    bt_report = stock_sub_agent.backtest_skill.run_backtest(
        start_date=state["backtest_start"],
        end_date=state["backtest_end"],
        stock_codes=state["stock_codes"]
    )
    state["backtest_report"] = bt_report
    state["step"] = "aggregate_result"
    return state

def aggregate_result_node(state: GlobalAgentState) -> GlobalAgentState:
    state["finished"] = True
    state["step"] = "finish"
    return state

def route_by_step(state: GlobalAgentState) -> str:
    return state["step"]

def build_agent_graph() -> StateGraph:
    graph = StateGraph(GlobalAgentState)
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("fetch_kline", fetch_kline_node)
    graph.add_node("stock_sub_infer", stock_sub_infer_node)
    graph.add_node("run_backtest", run_backtest_node)
    graph.add_node("aggregate_result", aggregate_result_node)
    graph.set_entry_point("orchestrator")
    graph.add_conditional_edges(
        source="orchestrator",
        path=route_by_step,
        path_map={
            "fetch_kline": "fetch_kline",
            "run_backtest": "run_backtest",
            "finish": END
        }
    )
    graph.add_edge("fetch_kline", "stock_sub_infer")
    graph.add_edge("stock_sub_infer", "aggregate_result")
    graph.add_edge("run_backtest", "aggregate_result")
    graph.add_edge("aggregate_result", END)
    return graph

stock_agent_graph = build_agent_graph().compile()

if __name__ == "__main__":
    test_single_state = GlobalAgentState(
        task_id="test_001",
        request_type="single_predict",
        stock_code="000001.SZ",
        window_end_date="2026-07-03",
        backtest_start=None,
        backtest_end=None,
        stock_codes=None,
        kline_window=None,
        predict_result=None,
        backtest_report=None,
        step="",
        error_info=None,
        finished=False
    )
    result = stock_agent_graph.invoke(test_single_state)
    print("Final output:", result)
