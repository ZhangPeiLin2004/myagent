


# Hermes Multi-Agent Architecture
## Overall Structure
1. Main Orchestrator (LangGraph orchestrator_node)
2. Stock Prediction Sub-Agent
3. Tool Layer: BaseTool + DataQueryTool
4. Skill Layer: ModelInferSkill, BacktestSkill
5. Memory Layer: Session persistent storage
6. MessageBus: Inter-agent communication

## Data Flow
User Input → FastAPI → LangGraph StateGraph
1. Orchestrator parse task type
2. Single Predict: Fetch 3-day kline → SubAgent inference → Return result
3. Backtest: Batch historical test → Output metrics report

## File Mapping
- graph.py: LangGraph state machine
- stock_predict_agent.py: Professional stock sub-agent
- base_tool.py: Unified tool abstract
- session_memory.py: Conversation persistence
- model_infer_skill.py: 3-day window ML prediction
