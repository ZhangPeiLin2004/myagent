
# Base tools for agent

# base_tool.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, Literal
import time
import logging

# 全局日志配置
logger = logging.getLogger("hermes_tool")

# 工具统一返回结构，所有工具必须输出该格式
@dataclass
class ToolReturn:
    success: bool
    data: Optional[Any]
    error_msg: Optional[str]
    cost_ms: int
    call_id: str

# 工具参数JSON Schema 标准结构（用于Hermes自动生成FunctionCall描述）
@dataclass
class ToolParamSchema:
    name: str
    type: Literal["string", "number", "integer", "boolean", "array", "object"]
    description: str
    required: bool
    default: Optional[Any] = None

# 所有工具父抽象类
class BaseTool(ABC):
    # 子类必须重写以下类属性
    name: str                   # 工具唯一标识，FunctionCall使用
    description: str            # LLM识别工具用途描述
    params_schema: list[ToolParamSchema]  # 参数定义，自动生成工具Prompt
    timeout: int = 10000        # 工具执行超时毫秒

    def __init__(self):
        self._call_id: Optional[str] = None

    def set_call_id(self, call_id: str) -> None:
        """绑定本次工具调用ID，用于链路追踪"""
        self._call_id = call_id

    def get_function_definition(self) -> Dict[str, Any]:
        """生成Hermes兼容的function call JSON定义，供LLM识别"""
        properties = {}
        required_list = []
        for p in self.params_schema:
            prop = {
                "type": p.type,
                "description": p.description
            }
            if p.default is not None:
                prop["default"] = p.default
            properties[p.name] = prop
            if p.required:
                required_list.append(p.name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required_list
            }
        }

    @abstractmethod
    def run(self, **kwargs) -> ToolReturn:
        """
        工具核心执行逻辑，子类重写
        kwargs: 从LLM FunctionCall解析出的参数字典
        return: ToolReturn 标准化结果
        """
        pass

    def execute(self, call_id: str, **kwargs) -> Dict[str, Any]:
        """
        对外统一调用入口：封装计时、异常捕获、标准化返回
        给Agent/Skill直接调用
        """
        self.set_call_id(call_id)
        start_ts = int(time.time() * 1000)
        try:
            # 执行子类实现的run逻辑
            result: ToolReturn = self.run(**kwargs)
        except Exception as e:
            logger.exception(f"Tool {self.name} run error, call_id={call_id}")
            cost = int(time.time() * 1000) - start_ts
            result = ToolReturn(
                success=False,
                data=None,
                error_msg=f"工具执行异常: {str(e)}",
                cost_ms=cost,
                call_id=call_id
            )

        cost = int(time.time() * 1000) - start_ts
        result.cost_ms = cost
        result.call_id = call_id
        # dataclass转字典，方便消息总线传输JSON
        return asdict(result)
