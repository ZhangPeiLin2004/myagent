


# stock_predict_agent

from dataclasses import dataclass
from typing import Optional
from backend.skill.model_infer_skill import Stock3DayInferSkill, PredictResult
from backend.tools.data_query_tool import DataQueryTool
from backend.skill.backtest_skill import BacktestSkill
from backend.common.msg_bus import MessageBus, AgentMessage

@dataclass
class StockPredictSubAgent:
    agent_id: str
    bus: MessageBus
    data_tool: DataQueryTool
    infer_skill: Stock3DayInferSkill
    backtest_skill: BacktestSkill

    def run_loop(self):
        while True:
            msg: Optional[AgentMessage] = self.bus.receive(self.agent_id)
            if not msg:
                continue
            self.handle_task(msg)

    def handle_task(self, msg: AgentMessage):
        task_content = msg.content
        task_type = task_content["task_type"]
        sender = msg.sender_id
        task_id = msg.task_id

        if task_type == "single_predict":
            code = task_content["stock_code"]
            end_dt = task_content["window_end_date"]
            tool_resp = self.data_tool.execute(call_id=task_id, stock_code=code, end_date=end_dt)
            if not tool_resp["success"]:
                self.send_error_msg(sender, task_id, tool_resp["error_msg"])
                return
            kline_window = tool_resp["data"]
            res: PredictResult = self.infer_skill.run(kline_window, code)
            reply_msg = AgentMessage(
                sender_id=self.agent_id,
                receiver_id=sender,
                task_id=task_id,
                msg_type="task_result",
                content={"predict_info": res.__dict__}
            )
            self.bus.send(reply_msg)

        elif task_type == "backtest":
            bt_start = task_content["backtest_start"]
            bt_end = task_content["backtest_end"]
            codes = task_content["target_codes"]
            bt_report = self.backtest_skill.run_backtest(bt_start, bt_end, codes)
            reply_msg = AgentMessage(
                sender_id=self.agent_id,
                receiver_id=sender,
                task_id=task_id,
                msg_type="task_result",
                content={"backtest_report": bt_report}
            )
            self.bus.send(reply_msg)

    def send_error_msg(self, target_id: str, task_id: str, err_msg: str):
        err_msg_obj = AgentMessage(
            sender_id=self.agent_id,
            receiver_id=target_id,
            task_id=task_id,
            msg_type="error",
            content={"error": err_msg},
            timestamp=""
        )
        self.bus.send(err_msg_obj)

