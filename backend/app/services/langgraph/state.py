from typing import TypedDict, Optional, List, Dict, Any
from langchain_core.messages import BaseMessage


class SchedulingState(TypedDict):
    query: str
    model: str
    session_id: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = []
    
    # === 工作流步骤结果 ===
    demand_forecast: Optional[str] = None
    inventory_check: Optional[Dict[str, Any]] = None
    inventory_optimization: Optional[str] = None
    scheduling_decision: Optional[str] = None
    cost_optimization: Optional[str] = None
    risk_control: Optional[str] = None
    risk_level: Optional[str] = None
    execution_control: Optional[str] = None
    
    # === 循环控制字段 ===
    iteration_count: int = 0
    tool_called: bool = False
    
    # === 执行记录 ===
    execution_history: List[Dict] = []
    final_summary: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = []
