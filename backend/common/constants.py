


# Global constant definitions
from typing import Literal

# Message type enums
MsgType = Literal["task_assign", "task_result", "feedback", "error"]

# Task types
TaskType = Literal["single_predict", "backtest"]

# Date format
DATE_FMT = "%Y-%m-%d"
