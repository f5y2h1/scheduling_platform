"""
LangGraph 工作流定义与编译
集成记忆系统、工具调用
体现 LangGraph 核心特点：条件分支、循环迭代、工具调用
"""
import uuid
from typing import Dict, Any, Optional, List

from langgraph.graph import StateGraph, END
from app.core.config import settings
from app.core.logger import logger
from .state import SchedulingState
from .nodes import (
    demand_forecast_node,
    inventory_check_node,
    inventory_optimization_node,
    scheduling_decision_node,
    cost_optimization_node,
    risk_control_node,
    execution_control_node,
    summary_node,
    tool_execution_node,
    should_replan,
    should_call_tool,
)
from .tools import get_all_tools


_checkpointer = None
_scheduling_workflow = None
_tools = None


def _get_checkpointer():
    global _checkpointer
    if _checkpointer is not None:
        return _checkpointer
    
    try:
        from langgraph.checkpoint.postgres import PostgresSaver
        _checkpointer = PostgresSaver.from_conn_string(
            settings.DATABASE_URL_SYNC,
            schema="langgraph"
        )
        logger.info("[LangGraph] PostgreSQL Checkpointer 初始化成功")
    except Exception as e:
        logger.warning(f"[LangGraph] Checkpointer 初始化失败，使用内存模式: {e}")
        _checkpointer = None
    
    return _checkpointer


def _get_tools():
    global _tools
    if _tools is not None:
        return _tools
    
    _tools = get_all_tools()
    
    return _tools


def _get_workflow():
    """延迟编译工作流 - 体现 LangGraph 循环特点"""
    global _scheduling_workflow
    if _scheduling_workflow is not None:
        return _scheduling_workflow
    
    checkpointer = _get_checkpointer()
    
    workflow = StateGraph(SchedulingState)
    
    # === 核心节点 ===
    workflow.add_node("demand_forecast", demand_forecast_node)
    workflow.add_node("inventory_check", inventory_check_node)
    workflow.add_node("inventory_optimization", inventory_optimization_node)
    workflow.add_node("scheduling_decision", scheduling_decision_node)
    workflow.add_node("cost_optimization", cost_optimization_node)
    workflow.add_node("risk_control", risk_control_node)
    workflow.add_node("execution_control", execution_control_node)
    workflow.add_node("summary", summary_node)
    
    # === 工具调用节点 ===
    workflow.add_node("tool_execution", tool_execution_node)
    
    # === 入口点 ===
    workflow.set_entry_point("demand_forecast")
    
    # === 线性流程 ===
    workflow.add_edge("demand_forecast", "inventory_check")
    workflow.add_edge("inventory_check", "inventory_optimization")
    workflow.add_edge("inventory_optimization", "scheduling_decision")
    workflow.add_edge("scheduling_decision", "cost_optimization")
    workflow.add_edge("cost_optimization", "risk_control")
    
    # === 条件分支 1: 是否需要重新规划 ===
    # 如果风险过高，回到调度决策重新制定方案（循环）
    workflow.add_conditional_edges(
        "risk_control",
        should_replan,
        {
            "replan": "scheduling_decision",
            "continue": "execution_control",
        }
    )
    
    # === 条件分支 2: 是否需要调用工具 ===
    # 在执行管控前，检查是否需要调用外部工具（如查询实时库存）
    workflow.add_conditional_edges(
        "execution_control",
        should_call_tool,
        {
            "call_tool": "tool_execution",
            "finish": "summary",
        }
    )
    
    # === 工具调用后回到执行管控（循环）===
    workflow.add_edge("tool_execution", "execution_control")
    
    # === 结束 ===
    workflow.add_edge("summary", END)
    
    _scheduling_workflow = workflow.compile(checkpointer=checkpointer)
    logger.info("[LangGraph] 工作流编译完成（含条件分支和循环）")
    
    return _scheduling_workflow


async def run_workflow(query: str, model: str | None = None,
                       session_id: str | None = None,
                       user_id: int = None) -> dict:
    import time
    t0 = time.time()

    logger.info(f"[LangGraph] 启动调度工作流, query={query[:50]}..., model={model}, session_id={session_id}")

    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info(f"[LangGraph] 生成新会话ID: {session_id}")

    initial_state: SchedulingState = {
        "query": query,
        "model": model or "qwen-plus",
        "session_id": session_id,
        "conversation_history": [],
        "execution_history": [],
        "tool_calls": [],
        "iteration_count": 0,
    }

    config = {"configurable": {"thread_id": session_id}}

    workflow = _get_workflow()
    result = await workflow.ainvoke(initial_state, config)

    elapsed = round((time.time() - t0) * 1000)
    iteration_count = result.get('iteration_count', 1)

    logger.info(f"[LangGraph] 调度工作流完成, session_id={session_id}, "
                f"迭代次数={iteration_count}, 耗时={elapsed}ms")

    # 记录执行经验到长期记忆
    try:
        from app.services.memory.memory_manager import memory_manager
        await memory_manager.record_execution(
            session_id=session_id,
            agent_name="scheduling_workflow",
            query=query,
            result=result.get("final_summary", ""),
            duration_ms=elapsed,
            iteration_count=iteration_count,
            tool_calls_count=len(result.get("tool_calls", [])),
        )
    except Exception as e:
        logger.warning(f"[LangGraph] 记录执行经验失败: {e}")

    return {
        "query": result["query"],
        "model": result["model"],
        "session_id": session_id,
        "steps": {
            "demand_forecast": result.get("demand_forecast"),
            "inventory_check": result.get("inventory_check"),
            "inventory_optimization": result.get("inventory_optimization"),
            "scheduling_decision": result.get("scheduling_decision"),
            "cost_optimization": result.get("cost_optimization"),
            "risk_control": result.get("risk_control"),
            "execution_control": result.get("execution_control"),
        },
        "summary": result.get("final_summary"),
        "execution_history": result.get("execution_history", []),
        "tool_calls": result.get("tool_calls", []),
        "iteration_count": iteration_count,
        "total_nodes": len(result.get("execution_history", [])),
        "elapsed_ms": elapsed,
    }


async def get_session_history(session_id: str) -> Optional[Dict[str, Any]]:
    checkpointer = _get_checkpointer()
    
    if not checkpointer:
        logger.warning("[LangGraph] Checkpointer 不可用")
        return None
    
    try:
        config = {"configurable": {"thread_id": session_id}}
        history = await checkpointer.aget_history(config)
        
        if history:
            return {
                "session_id": session_id,
                "history": [h for h in history],
                "count": len(list(history)),
            }
        return None
    except Exception as e:
        logger.error(f"[LangGraph] 获取会话历史失败: {e}")
        return None


async def list_sessions() -> list:
    checkpointer = _get_checkpointer()
    
    if not checkpointer:
        return []
    
    try:
        sessions = []
        async for config in checkpointer.aget_configs():
            sessions.append({
                "thread_id": config.get("configurable", {}).get("thread_id"),
                "created_at": config.get("created_at"),
            })
        return sessions
    except Exception as e:
        logger.error(f"[LangGraph] 获取会话列表失败: {e}")
        return []


async def delete_session(session_id: str) -> bool:
    checkpointer = _get_checkpointer()
    
    if not checkpointer:
        return False
    
    try:
        config = {"configurable": {"thread_id": session_id}}
        await checkpointer.adelete(config)
        logger.info(f"[LangGraph] 删除会话成功: {session_id}")
        return True
    except Exception as e:
        logger.error(f"[LangGraph] 删除会话失败: {e}")
        return False


def get_available_tools() -> list:
    tools = _get_tools()
    tool_list = []
    
    for tool_obj in tools:
        tool_info = {
            "name": tool_obj.name,
            "description": tool_obj.description,
            "args_schema": tool_obj.args_schema.schema() if hasattr(tool_obj, 'args_schema') else {},
        }
        tool_list.append(tool_info)
    
    return tool_list
