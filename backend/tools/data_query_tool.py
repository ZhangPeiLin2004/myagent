

# Data Query

# tools/data_query_tool.py
from backend.tools.base_tool import BaseTool, ToolParamSchema, ToolReturn
from backend.db.kline_db import AShareKlineDB

class DataQueryTool(BaseTool):
    name = "get_3day_kline"
    description = "根据股票代码与结束日期，查询连续3日A股日线行情(t-2, t-1, t)，用于3日窗口模型预测"
    timeout = 15000
    params_schema = [
        ToolParamSchema(
            name="stock_code",
            type="string",
            description="沪深A股股票代码，如000001.SZ、600036.SH",
            required=True
        ),
        ToolParamSchema(
            name="end_date",
            type="string",
            description="窗口结束日期，格式YYYY-MM-DD，将自动向前取t-2、t-1、t三天",
            required=True
        )
    ]

    def __init__(self):
        super().__init__()
        self.db = AShareKlineDB()

    def run(self, stock_code: str, end_date: str) -> ToolReturn:
        kline_list = self.db.query_three_day_window(code=stock_code, end_dt=end_date)
        if len(kline_list) != 3:
            return ToolReturn(
                success=False,
                data=kline_list,
                error_msg=f"行情数据不足3条，仅获取到{len(kline_list)}条，存在停牌或日期越界",
                cost_ms=0,
                call_id=self._call_id
            )
        return ToolReturn(
            success=True,
            data=kline_list,
            error_msg=None,
            cost_ms=0,
            call_id=self._call_id
        )
