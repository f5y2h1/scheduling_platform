"""
LangGraph 节点定义
包含条件分支和循环逻辑
"""
from typing import Any, Dict
from app.core.logger import logger
from app.services.ai.agent_orchestrator import orchestrator
from .tools import get_all_tools


# === 核心业务节点 ===

async def demand_forecast_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("[LangGraph] 执行需求预测节点")
    query = state.get("query", "")
    model = state.get("model")
    
    result = await orchestrator.invoke_agent("demand_forecast", model, query)
    
    return {
        "demand_forecast": result.get("result", ""),
        "execution_history": state.get("execution_history", []) + [{
            "node": "demand_forecast",
            "status": "completed",
            "timestamp": result.get("timestamp"),
        }],
        "iteration_count": state.get("iteration_count", 0) + 1,
    }


async def inventory_check_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """检查当前库存状态（调用工具）"""
    logger.info("[LangGraph] 执行库存检查节点")
    
    from .tools import query_inventory
    demand_result = state.get("demand_forecast", "")
    
    try:
        inventory_data = await query_inventory()
        
        low_stock_items = [item for item in inventory_data 
                          if item.get("available_quantity", 0) <= item.get("safety_stock", 0)]
        
        check_result = {
            "total_items": len(inventory_data),
            "low_stock_count": len(low_stock_items),
            "low_stock_items": low_stock_items,
            "inventory_summary": f"当前库存共{len(inventory_data)}种商品，其中{len(low_stock_items)}种低于安全库存",
        }
        
        return {
            "inventory_check": check_result,
            "execution_history": state.get("execution_history", []) + [{
                "node": "inventory_check",
                "status": "completed",
                "tool_called": "query_inventory",
            }],
        }
    except Exception as e:
        logger.error(f"[LangGraph] 库存检查失败: {e}")
        return {
            "inventory_check": {"error": str(e)},
            "execution_history": state.get("execution_history", []) + [{
                "node": "inventory_check",
                "status": "failed",
            }],
        }


async def inventory_optimization_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("[LangGraph] 执行库存优化节点")
    demand_result = state.get("demand_forecast", "")
    inventory_check = state.get("inventory_check", {})
    model = state.get("model")
    
    query = f"""基于需求预测和库存检查结果给出库存优化建议:
    
需求预测:
{demand_result}

库存检查:
{inventory_check.get('inventory_summary', '')}
低库存商品: {[item.get('product_name') for item in inventory_check.get('low_stock_items', [])]}
"""
    
    result = await orchestrator.invoke_agent("inventory_optimization", model, query)
    
    return {
        "inventory_optimization": result.get("result", ""),
        "execution_history": state.get("execution_history", []) + [{
            "node": "inventory_optimization",
            "status": "completed",
            "timestamp": result.get("timestamp"),
        }],
    }


async def scheduling_decision_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("[LangGraph] 执行调度决策节点")
    inventory_result = state.get("inventory_optimization", "")
    model = state.get("model")
    
    query = f"基于库存方案制定调度计划:\n{inventory_result}"
    result = await orchestrator.invoke_agent("scheduling_decision", model, query)
    
    return {
        "scheduling_decision": result.get("result", ""),
        "execution_history": state.get("execution_history", []) + [{
            "node": "scheduling_decision",
            "status": "completed",
            "timestamp": result.get("timestamp"),
        }],
    }


async def cost_optimization_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("[LangGraph] 执行成本优化节点")
    scheduling_result = state.get("scheduling_decision", "")
    model = state.get("model")
    
    query = f"核算调度方案成本:\n{scheduling_result}"
    result = await orchestrator.invoke_agent("cost_optimization", model, query)
    
    return {
        "cost_optimization": result.get("result", ""),
        "execution_history": state.get("execution_history", []) + [{
            "node": "cost_optimization",
            "status": "completed",
            "timestamp": result.get("timestamp"),
        }],
    }


async def risk_control_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("[LangGraph] 执行风险控制节点")
    demand_result = state.get("demand_forecast", "")
    scheduling_result = state.get("scheduling_decision", "")
    cost_result = state.get("cost_optimization", "")
    model = state.get("model")
    
    query = f"""评估方案风险并给出风险等级(高/中/低):
    
需求预测: {demand_result[:100]}...
调度方案: {scheduling_result[:100]}...
成本核算: {cost_result[:100]}...
"""
    
    result = await orchestrator.invoke_agent("risk_control", model, query)
    risk_result = result.get("result", "")
    
    risk_level = "medium"
    if "高" in risk_result or "严重" in risk_result:
        risk_level = "high"
    elif "低" in risk_result or "安全" in risk_result:
        risk_level = "low"
    
    return {
        "risk_control": risk_result,
        "risk_level": risk_level,
        "execution_history": state.get("execution_history", []) + [{
            "node": "risk_control",
            "status": "completed",
            "risk_level": risk_level,
            "timestamp": result.get("timestamp"),
        }],
    }


async def execution_control_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("[LangGraph] 执行执行管控节点")
    scheduling_result = state.get("scheduling_decision", "")
    cost_result = state.get("cost_optimization", "")
    risk_result = state.get("risk_control", "")
    model = state.get("model")
    
    query = f"""生成执行计划:
    
调度方案: {scheduling_result[:200]}...
成本核算: {cost_result[:100]}...
风险评估: {risk_result[:100]}...
"""
    
    result = await orchestrator.invoke_agent("execution_control", model, query)
    
    return {
        "execution_control": result.get("result", ""),
        "execution_history": state.get("execution_history", []) + [{
            "node": "execution_control",
            "status": "completed",
            "timestamp": result.get("timestamp"),
        }],
    }


async def summary_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("[LangGraph] 执行总结节点")
    
    summary = f"""# 供应链智能调度方案总结

## 📊 需求预测
{state.get('demand_forecast', '未完成')[:300]}...

## 📦 库存检查
{state.get('inventory_check', {}).get('inventory_summary', '未完成')}

## 🔄 库存优化
{state.get('inventory_optimization', '未完成')[:300]}...

## 🚚 调度决策
{state.get('scheduling_decision', '未完成')[:300]}...

## 💰 成本优化
{state.get('cost_optimization', '未完成')[:200]}...

## ⚠️ 风险控制
风险等级: {state.get('risk_level', '未知')}
{state.get('risk_control', '未完成')[:200]}...

## 📋 执行计划
{state.get('execution_control', '未完成')[:300]}...

---
📈 迭代次数: {state.get('iteration_count', 1)}
"""
    
    return {
        "final_summary": summary,
        "execution_history": state.get("execution_history", []) + [{
            "node": "summary",
            "status": "completed",
        }],
    }


# === 工具调用节点 ===

async def tool_execution_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    工具执行节点 - 根据状态调用相应的业务工具
    体现 LangGraph 的工具调用能力
    """
    logger.info("[LangGraph] 执行工具调用节点")
    
    execution_plan = state.get("execution_control", "")
    
    tool_calls_made = []
    
    if "库存" in execution_plan or "入库" in execution_plan:
        try:
            from .tools import query_inventory, query_low_stock
            low_stock = await query_low_stock()
            tool_calls_made.append({
                "tool": "query_low_stock",
                "result": f"查询到 {len(low_stock)} 种低库存商品",
            })
            logger.info(f"[LangGraph] 调用工具 query_low_stock, 结果: {len(low_stock)} 条")
        except Exception as e:
            logger.error(f"[LangGraph] 工具调用失败: {e}")
    
    if "订单" in execution_plan:
        try:
            from .tools import query_orders
            orders = await query_orders(status="PENDING")
            tool_calls_made.append({
                "tool": "query_orders",
                "result": f"查询到 {len(orders)} 个待处理订单",
            })
            logger.info(f"[LangGraph] 调用工具 query_orders, 结果: {len(orders)} 条")
        except Exception as e:
            logger.error(f"[LangGraph] 工具调用失败: {e}")
    
    if "供应商" in execution_plan:
        try:
            from .tools import query_suppliers
            suppliers = await query_suppliers()
            tool_calls_made.append({
                "tool": "query_suppliers",
                "result": f"查询到 {len(suppliers)} 个供应商",
            })
            logger.info(f"[LangGraph] 调用工具 query_suppliers, 结果: {len(suppliers)} 条")
        except Exception as e:
            logger.error(f"[LangGraph] 工具调用失败: {e}")
    
    return {
        "tool_calls": state.get("tool_calls", []) + tool_calls_made,
        "execution_history": state.get("execution_history", []) + [{
            "node": "tool_execution",
            "status": "completed",
            "tools_called": [tc["tool"] for tc in tool_calls_made],
        }],
    }


# === 条件分支函数（体现循环特点）===

def should_replan(state: Dict[str, Any]) -> str:
    """
    条件分支函数：判断是否需要重新规划
    
    如果风险等级为高，则回到调度决策节点重新制定方案
    否则继续执行后续流程
    
    Returns:
        "replan" - 需要重新规划（循环）
        "continue" - 继续执行
    """
    risk_level = state.get("risk_level", "medium")
    iteration_count = state.get("iteration_count", 0)
    
    logger.info(f"[LangGraph] 条件判断: risk_level={risk_level}, iteration_count={iteration_count}")
    
    if risk_level == "high" and iteration_count < 3:
        logger.info("[LangGraph] 风险过高，触发重新规划循环")
        return "replan"
    
    return "continue"


def should_call_tool(state: Dict[str, Any]) -> str:
    """
    条件分支函数：判断是否需要调用外部工具
    
    根据执行计划内容决定是否调用工具
    工具调用后会回到执行管控节点（循环）
    
    Returns:
        "call_tool" - 需要调用工具（循环）
        "finish" - 直接结束
    """
    execution_plan = state.get("execution_control", "")
    tool_called = state.get("tool_called", False)
    
    if tool_called:
        logger.info("[LangGraph] 工具已调用，跳过循环")
        return "finish"
    
    needs_tool = any(keyword in execution_plan for keyword in ["库存", "订单", "供应商", "物流"])
    
    if needs_tool:
        logger.info("[LangGraph] 执行计划需要工具支持，触发工具调用")
        return "call_tool"
    
    return "finish"
