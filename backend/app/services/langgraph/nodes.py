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
    result = {}
    timestamp = None

    try:
        result = await orchestrator.invoke_agent("demand_forecast", model, query)
        content = result.get("result", "")
        timestamp = result.get("timestamp")
        status = "completed" if content and len(content) > 50 else "partial"
        if not content:
            logger.warning("[LangGraph] 需求预测节点返回空结果，API 可能未配置或密钥无效")
    except Exception as e:
        logger.error(f"[LangGraph] 需求预测节点异常: {e}")
        content = f"执行异常: {str(e)}"
        status = "failed"

    return {
        "demand_forecast": content,
        "execution_history": state.get("execution_history", []) + [{
            "node": "demand_forecast",
            "status": status,
            "timestamp": timestamp,
        }],
        "iteration_count": state.get("iteration_count", 0) + 1,
    }


async def inventory_check_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """检查当前库存状态（调用工具）"""
    logger.info("[LangGraph] 执行库存检查节点")

    from .tools import query_inventory

    try:
        # LangChain @tool 装饰的异步函数必须通过 .ainvoke() 调用
        result = await query_inventory.ainvoke({})
        items = result.get("data", []) if isinstance(result, dict) else []

        if not items:
            logger.warning("[LangGraph] 库存查询返回空数据")
            return {
                "inventory_check": {
                    "total_items": 0,
                    "low_stock_count": 0,
                    "low_stock_items": [],
                    "inventory_summary": "未查询到库存数据，数据库可能为空",
                },
                "execution_history": state.get("execution_history", []) + [{
                    "node": "inventory_check",
                    "status": "partial",
                    "tool_called": "query_inventory",
                }],
            }

        low_stock_items = [
            item for item in items
            if item.get("available_quantity", 0) <= item.get("safety_stock", 0)
        ]

        check_result = {
            "total_items": len(items),
            "low_stock_count": len(low_stock_items),
            "low_stock_items": low_stock_items,
            "all_items": items,
            "inventory_summary": (
                f"当前库存共 {len(items)} 种商品，"
                f"其中 {len(low_stock_items)} 种低于安全库存"
            ),
        }

        # 构建库存数据文本供后续 Agent 分析
        inventory_text_lines = ["## 各仓库库存明细\n"]
        for item in items:
            inv_text = (
                f"- {item['product_name']} ({item['sku_code']}) | "
                f"仓库: {item['warehouse_name']} | "
                f"库存: {item['quantity']} | "
                f"可用: {item['available_quantity']} | "
                f"安全库存: {item['safety_stock']} | "
                f"状态: {item['status']}"
            )
            inventory_text_lines.append(inv_text)

        check_result["inventory_detail_text"] = "\n".join(inventory_text_lines)

        logger.info(f"[LangGraph] 库存检查完成: total={len(items)}, low_stock={len(low_stock_items)}")

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
            "inventory_check": {"error": str(e), "total_items": 0, "low_stock_count": 0,
                                "low_stock_items": [], "inventory_summary": f"查询失败: {e}"},
            "execution_history": state.get("execution_history", []) + [{
                "node": "inventory_check", "status": "failed",
            }],
        }


async def inventory_optimization_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("[LangGraph] 执行库存优化节点")
    demand_result = state.get("demand_forecast", "")
    inventory_check = state.get("inventory_check", {})
    model = state.get("model")
    result = {}
    timestamp = None

    # 将数据库真实库存数据注入提示词
    inv_detail = inventory_check.get("inventory_detail_text", "")
    inv_summary = inventory_check.get("inventory_summary", "")
    low_items = inventory_check.get("low_stock_items", [])

    query = f"""基于需求预测和以下真实库存数据，给出库存优化建议：

## 需求预测
{demand_result[:600] if demand_result else '（需求预测未完成，请基于库存数据本身给出建议）'}

## 真实库存数据（来自数据库实时查询）
{inv_detail if inv_detail else inv_summary}

## 低库存商品（可用库存 ≤ 安全库存）
共 {len(low_items)} 种：
{chr(10).join(f'- {i.get("product_name", "?")}: 可用 {i.get("available_quantity", 0)} / 安全库存 {i.get("safety_stock", 0)} / 缺口 {max(0, i.get("safety_stock", 0) - i.get("available_quantity", 0))} 件' for i in low_items) if low_items else '无'}

请给出具体的补货/调拨建议，包含补货数量、优先级和理由。"""
    try:
        result = await orchestrator.invoke_agent("inventory_optimization", model, query)
        content = result.get("result", "")
        timestamp = result.get("timestamp")
        status = "completed" if content and len(content) > 20 else "partial"
    except Exception as e:
        logger.error(f"[LangGraph] 库存优化节点异常: {e}")
        content = f"执行异常: {str(e)}"
        status = "failed"

    return {
        "inventory_optimization": content,
        "execution_history": state.get("execution_history", []) + [{
            "node": "inventory_optimization",
            "status": status,
            "timestamp": timestamp,
        }],
    }


async def scheduling_decision_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("[LangGraph] 执行调度决策节点")
    inventory_result = state.get("inventory_optimization", "")
    inventory_check = state.get("inventory_check", {})
    model = state.get("model")
    result = {}
    timestamp = None

    inv_detail = inventory_check.get("inventory_detail_text", "")
    query = f"""基于库存优化建议和真实库存数据，制定具体的调度/调拨计划:

## 库存优化建议
{inventory_result[:600] if inventory_result else '（上一步未完成）'}

## 当前库存分布（实时数据库数据）
{inv_detail[:800] if inv_detail else '无库存数据'}

请制定具体方案：调拨来源仓库、目标仓库、调拨商品和数量、优先级排序。"""
    try:
        result = await orchestrator.invoke_agent("scheduling_decision", model, query)
        content = result.get("result", "")
        timestamp = result.get("timestamp")
        status = "completed" if content and len(content) > 20 else "partial"
    except Exception as e:
        logger.error(f"[LangGraph] 调度决策节点异常: {e}")
        content = f"执行异常: {str(e)}"
        status = "failed"

    return {
        "scheduling_decision": content,
        "execution_history": state.get("execution_history", []) + [{
            "node": "scheduling_decision",
            "status": status,
            "timestamp": timestamp,
        }],
    }


async def cost_optimization_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("[LangGraph] 执行成本优化节点")
    scheduling_result = state.get("scheduling_decision", "")
    inventory_check = state.get("inventory_check", {})
    model = state.get("model")
    result = {}
    timestamp = None

    inv_detail = inventory_check.get("inventory_detail_text", "")
    low_items = inventory_check.get("low_stock_items", [])
    query = f"""核算以下调度方案的物流成本，基于真实库存缺口评估:

## 调度方案
{scheduling_result[:500] if scheduling_result else '（上一步未完成）'}

## 库存数据参考
{inv_detail[:500] if inv_detail else '无'}
低库存商品数: {len(low_items) if isinstance(low_items, list) else 0}

请给出运输成本估算、最优路线建议和总成本核算。"""
    try:
        result = await orchestrator.invoke_agent("cost_optimization", model, query)
        content = result.get("result", "")
        timestamp = result.get("timestamp")
        status = "completed" if content and len(content) > 20 else "partial"
    except Exception as e:
        logger.error(f"[LangGraph] 成本优化节点异常: {e}")
        content = f"执行异常: {str(e)}"
        status = "failed"

    return {
        "cost_optimization": content,
        "execution_history": state.get("execution_history", []) + [{
            "node": "cost_optimization",
            "status": status,
            "timestamp": timestamp,
        }],
    }


async def risk_control_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("[LangGraph] 执行风险控制节点")
    demand_result = state.get("demand_forecast", "")
    scheduling_result = state.get("scheduling_decision", "")
    cost_result = state.get("cost_optimization", "")
    model = state.get("model")
    result = {}
    timestamp = None

    query = f"""评估方案风险并给出风险等级(高/中/低):

需求预测: {demand_result[:100]}...
调度方案: {scheduling_result[:100]}...
成本核算: {cost_result[:100]}...
"""

    try:
        result = await orchestrator.invoke_agent("risk_control", model, query)
        risk_result = result.get("result", "")
        timestamp = result.get("timestamp")

        risk_level = "medium"
        if "高" in risk_result or "严重" in risk_result:
            risk_level = "high"
        elif "低" in risk_result or "安全" in risk_result:
            risk_level = "low"
        status = "completed" if risk_result else "partial"
    except Exception as e:
        logger.error(f"[LangGraph] 风险控制节点异常: {e}")
        risk_result = f"执行异常: {str(e)}"
        risk_level = "unknown"
        status = "failed"

    return {
        "risk_control": risk_result,
        "risk_level": risk_level,
        "execution_history": state.get("execution_history", []) + [{
            "node": "risk_control",
            "status": status,
            "risk_level": risk_level,
            "timestamp": timestamp,
        }],
    }


async def execution_control_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("[LangGraph] 执行执行管控节点")
    scheduling_result = state.get("scheduling_decision", "")
    cost_result = state.get("cost_optimization", "")
    risk_result = state.get("risk_control", "")
    model = state.get("model")
    result = {}
    timestamp = None

    query = f"""生成执行计划:

调度方案: {scheduling_result[:200]}...
成本核算: {cost_result[:100]}...
风险评估: {risk_result[:100]}...
"""

    try:
        result = await orchestrator.invoke_agent("execution_control", model, query)
        content = result.get("result", "")
        timestamp = result.get("timestamp")
        status = "completed" if content and len(content) > 20 else "partial"
    except Exception as e:
        logger.error(f"[LangGraph] 执行管控节点异常: {e}")
        content = f"执行异常: {str(e)}"
        status = "failed"

    return {
        "execution_control": content,
        "execution_history": state.get("execution_history", []) + [{
            "node": "execution_control",
            "status": status,
            "timestamp": timestamp,
        }],
    }


async def summary_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("[LangGraph] 执行总结节点")

    # 收集各节点数据
    demand = state.get('demand_forecast', '') or ''
    inv_check = state.get('inventory_check', {}) or {}
    inv_opt = state.get('inventory_optimization', '') or ''
    scheduling = state.get('scheduling_decision', '') or ''
    cost = state.get('cost_optimization', '') or ''
    risk = state.get('risk_control', '') or ''
    risk_level = state.get('risk_level', 'medium')
    execution = state.get('execution_control', '') or ''
    tool_calls = state.get('tool_calls', [])
    iterations = state.get('iteration_count', 1)
    exec_hist = state.get('execution_history', [])

    # 统计执行状态
    completed_nodes = [h['node'] for h in exec_hist if h.get('status') == 'completed']
    total_nodes = len(exec_hist)

    # 构建库存检查摘要（直接使用数据库真实数据）
    inv_section = "未执行库存检查"
    if inv_check:
        total_items = inv_check.get('total_items', 0)
        low_count = inv_check.get('low_stock_count', 0)
        low_items = inv_check.get('low_stock_items', [])
        all_items = inv_check.get('all_items', [])
        summary_text = inv_check.get('inventory_summary', '')
        inv_section = f"""**{summary_text}**

| 指标 | 数值 |
|------|------|
| 商品种类总数 | {total_items} |
| 低库存商品数 | {low_count} |

"""
        # 展示全部库存表格
        if all_items:
            inv_section += "**全部库存明细：**\n\n"
            inv_section += "| 商品 | SKU | 仓库 | 库存 | 可用 | 安全库存 | 状态 |\n"
            inv_section += "|------|-----|------|------|------|----------|------|\n"
            for item in all_items[:20]:
                inv_section += (
                    f"| {item.get('product_name', '?')} "
                    f"| {item.get('sku_code', '?')} "
                    f"| {item.get('warehouse_name', '?')} "
                    f"| {item.get('quantity', 0)} "
                    f"| {item.get('available_quantity', 0)} "
                    f"| {item.get('safety_stock', 0)} "
                    f"| {item.get('status', '?')} |\n"
                )

        if low_items:
            inv_section += "\n**⚠️ 低库存商品（需要优先处理）：**\n\n"
            for item in low_items[:10]:
                shortage = max(0, item.get('safety_stock', 0) - item.get('available_quantity', 0))
                inv_section += (
                    f"- **{item.get('product_name', '?')}** ({item.get('warehouse_name', '?')}) | "
                    f"可用: {item.get('available_quantity', 0)} / "
                    f"安全库存: {item.get('safety_stock', 0)} | "
                    f"缺口: **{shortage} 件**\n"
                )

    # 构建工具调用摘要
    tool_section = "未调用工具"
    if tool_calls:
        tool_lines = []
        for tc in tool_calls:
            t_name = tc.get('tool', '?')
            t_result = tc.get('result', '')
            t_success = '✅' if (isinstance(t_result, dict) and t_result.get('success')) else '⚠️'
            msg = t_result.get('message', str(t_result)[:100]) if isinstance(t_result, dict) else str(t_result)[:100]
            tool_lines.append(f"- {t_success} **{t_name}**: {msg}")
        tool_section = "\n".join(tool_lines)

    summary = f"""# 📋 供应链智能调度方案总结

## 📊 执行概览

| 指标 | 值 |
|------|-----|
| 迭代次数 | {iterations} |
| 执行节点数 | {total_nodes} |
| 风险等级 | **{risk_level.upper()}** |
| 工具调用次数 | {len(tool_calls)} |

---

## 📦 库存检查

{inv_section}

---

## 📊 需求预测

{demand[:500] if demand else '> ⚠️ AI 需求预测未返回结果，请检查 API 密钥配置或重试'}

---

## 🔄 库存优化建议

{inv_opt[:500] if inv_opt else '> ⚠️ AI 库存优化未返回结果'}

---

## 🚚 调度决策

{scheduling[:500] if scheduling else '> ⚠️ AI 调度决策未返回结果'}

---

## 💰 成本核算

{cost[:400] if cost else '> ⚠️ AI 成本分析未返回结果'}

---

## ⚠️ 风险控制

**风险等级: {risk_level.upper()}**

{risk[:400] if risk else '> ⚠️ AI 风险评估未返回结果'}

---

## 📋 执行计划

{execution[:400] if execution else '> ⚠️ AI 执行计划未返回结果'}

---

## 🔧 工具调用记录

{tool_section}

---

*报告生成时间: 自动生成 | 迭代次数: {iterations} | 工作流引擎: LangGraph*
"""
    return {
        "final_summary": summary.strip(),
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
            result = await query_low_stock.ainvoke({})
            count = result.get("total", len(result.get("data", []))) if isinstance(result, dict) else 0
            tool_calls_made.append({
                "tool": "query_low_stock",
                "result": f"查询到 {count} 种低库存商品",
            })
            logger.info(f"[LangGraph] 调用工具 query_low_stock, 结果: {count} 条")
        except Exception as e:
            logger.error(f"[LangGraph] 工具调用失败: {e}")

    if "订单" in execution_plan:
        try:
            from .tools import query_orders
            result = await query_orders.ainvoke({"status": "PENDING"})
            count = result.get("total", len(result.get("data", []))) if isinstance(result, dict) else 0
            tool_calls_made.append({
                "tool": "query_orders",
                "result": f"查询到 {count} 个待处理订单",
            })
            logger.info(f"[LangGraph] 调用工具 query_orders, 结果: {count} 条")
        except Exception as e:
            logger.error(f"[LangGraph] 工具调用失败: {e}")

    if "供应商" in execution_plan:
        try:
            from .tools import query_suppliers
            result = await query_suppliers.ainvoke({})
            count = result.get("total", len(result.get("data", []))) if isinstance(result, dict) else 0
            tool_calls_made.append({
                "tool": "query_suppliers",
                "result": f"查询到 {count} 个供应商",
            })
            logger.info(f"[LangGraph] 调用工具 query_suppliers, 结果: {count} 条")
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
