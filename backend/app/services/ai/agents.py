"""
6大业务 Agent
每个 Agent = 系统提示词 + 知识库检索 + LLM推理
"""
import json
from abc import ABC, abstractmethod

from app.core.config import settings
from app.core.logger import logger
from app.services.ai.bailian_client import bailian_client
from app.services.rag.knowledge_base import kb_service


class BaseAgent(ABC):
    """Agent 基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def system_prompt(self) -> str:
        """系统提示词"""
        ...

    def focus_category(self) -> str | None:
        """关注的知识分类"""
        return None

    def tool_description(self) -> str:
        return "可用工具：知识库检索、数据分析工具"

    async def think(self, query: str, model: str | None = None) -> str:
        """Agent推理（支持 Function Calling）"""
        logger.info(f"[{self.name}] 推理中, model={model}")

        # 1. 检索知识
        knowledge = await self._retrieve_knowledge(query)

        # 2. 获取可用工具
        tools = self._get_available_tools()

        # 3. 构建完整prompt
        prompt = f"""# 角色定义
{self.system_prompt()}

"""
        if knowledge:
            prompt += f"# 📚 相关知识库\n{knowledge}\n\n"
        prompt += """你可以根据需要调用工具来获取真实数据。
如果需要查询库存、订单、供应商等信息，请调用相应的工具。
如果工具返回了数据，请基于数据进行分析和回答。
如果不需要调用工具，可以直接回答用户的问题。"""

        # 4. 调用LLM（支持工具调用）
        messages = [{"role": "system", "content": prompt}, {"role": "user", "content": query}]
        resp = bailian_client.chat(messages, model=model, tools=tools)

        # 5. 处理工具调用
        if resp.get("tool_calls") and len(resp["tool_calls"]) > 0:
            logger.info(f"[{self.name}] 模型请求调用工具: {resp['tool_calls']}")
            
            tool_results = []
            for tool_call in resp["tool_calls"]:
                tool_name = tool_call.get("name")
                arguments = tool_call.get("arguments", {})
                
                result = await self._execute_tool(tool_name, arguments)
                tool_results.append({
                    "tool": tool_name,
                    "arguments": arguments,
                    "result": result,
                })
            
            # 将工具结果作为新消息发送给模型
            tool_result_content = "\n\n".join([
                f"工具调用结果 [{tr['tool']}]: {json.dumps(tr['result'], ensure_ascii=False)}"
                for tr in tool_results
            ])
            
            messages.append({"role": "assistant", "content": resp.get("content", "")})
            messages.append({"role": "user", "content": f"工具调用结果如下，请基于这些数据进行分析和回答：\n{tool_result_content}"})
            
            resp = bailian_client.chat(messages, model=model, tools=tools)

        # 6. 记录决策
        await self._record_decision(query, resp.get("content", ""))

        return resp.get("content", "")
    
    def _get_available_tools(self) -> list:
        """获取可用工具列表"""
        try:
            from app.services.langgraph.workflow import get_available_tools
            return get_available_tools()
        except Exception as e:
            logger.warning(f"[{self.name}] 获取工具列表失败: {e}")
            return []
    
    async def _execute_tool(self, tool_name: str, arguments: dict) -> any:
        """执行工具调用"""
        try:
            from app.services.langgraph.tools import (
                query_inventory, query_low_stock, query_orders, 
                query_suppliers, stock_in_operation, stock_out_operation
            )
            
            tool_map = {
                "query_inventory": query_inventory,
                "query_low_stock": query_low_stock,
                "query_orders": query_orders,
                "query_suppliers": query_suppliers,
                "stock_in_operation": stock_in_operation,
                "stock_out_operation": stock_out_operation,
            }
            
            tool_func = tool_map.get(tool_name)
            if not tool_func:
                logger.warning(f"[{self.name}] 未知工具: {tool_name}")
                return {"error": f"未知工具: {tool_name}"}
            
            logger.info(f"[{self.name}] 执行工具: {tool_name}, 参数: {arguments}")
            result = await tool_func(**arguments)
            logger.info(f"[{self.name}] 工具执行完成: {tool_name}, 结果: {result}")
            
            return result
        except Exception as e:
            logger.error(f"[{self.name}] 工具执行失败: {tool_name}, 错误: {e}")
            return {"error": str(e)}

    async def _retrieve_knowledge(self, query: str) -> str:
        """RAG知识检索"""
        try:
            category = self.focus_category()
            if category:
                docs = kb_service.category_search(query, category, top_k=3)
            else:
                docs = kb_service.hybrid_search(query, top_k=3)

            if not docs:
                return ""

            parts = []
            for i, d in enumerate(docs):
                p = d.get("payload", {})
                parts.append(
                    f"【知识{i + 1}】(相关度:{d['score']:.0%}, 来源:{p.get('category', '')})\n"
                    f"{p.get('content', '')}"
                )
            return "\n\n".join(parts)
        except Exception as e:
            logger.warning(f"[{self.name}] 知识检索异常: {e}")
            return ""

    async def _record_decision(self, query: str, result: str):
        """记录决策到向量库"""
        try:
            kb_service.record_decision(
                f"{self.name}: {query}",
                result[:500] if len(result) > 500 else result,
                "success",
                {"agent": self.name, "query": query},
            )
        except Exception:
            pass


# ==================== 6个具体Agent ====================

class DemandForecastAgent(BaseAgent):
    def __init__(self):
        super().__init__("需求预测Agent", "基于历史订单与市场趋势，预测商品需求量")

    def system_prompt(self) -> str:
        return """你是资深供应链需求预测专家。你擅长：
1. 分析历史销售数据，识别销量趋势和季节性规律
2. 结合市场因素（促销活动、节假日、行业趋势）进行需求预测
3. 使用时间序列分析，给出未来1-4周需求量预测
4. 识别异常需求波动并提供预警"""

    def focus_category(self) -> str | None:
        return "需求预测"


class InventoryOptimizationAgent(BaseAgent):
    def __init__(self):
        super().__init__("库存优化Agent", "基于库存水平与需求预测，生成补货与库存配置方案")

    def system_prompt(self) -> str:
        return """你是库存优化专家。你擅长：
1. 基于需求预测计算安全库存和再订货点
2. 平衡库存持有成本与缺货风险
3. 识别滞销品和过剩库存，提出去库存建议
4. 制定分仓补货计划"""

    def focus_category(self) -> str | None:
        return "库存策略"


class SchedulingDecisionAgent(BaseAgent):
    def __init__(self):
        super().__init__("调度决策Agent", "根据订单、库存、运力信息，生成最优调度方案")

    def system_prompt(self) -> str:
        return """你是调度决策专家。你擅长：
1. 根据订单分布、库存量、运力做多仓调度决策
2. 优化运输路径，降低物流成本
3. 在突发情况下快速调整方案
4. 生成多套方案并对比优劣"""

    def focus_category(self) -> str | None:
        return "调度规则"


class CostOptimizationAgent(BaseAgent):
    def __init__(self):
        super().__init__("成本优化Agent", "核算方案成本，进行方案对比与最优推荐")

    def system_prompt(self) -> str:
        return """你是供应链成本分析专家。你擅长：
1. 全面核算调度方案总成本
2. 识别成本优化空间
3. 对比多套方案成本效益
4. 做盈亏平衡与敏感度分析"""

    def focus_category(self) -> str | None:
        return "成本优化"


class RiskControlAgent(BaseAgent):
    def __init__(self):
        super().__init__("风险控制Agent", "识别供应链各环节风险，输出预警与处置建议")

    def system_prompt(self) -> str:
        return """你是供应链风险管理专家。你擅长：
1. 识别订单履约链路的各类风险
2. 评估风险等级和影响范围
3. 制定风险应对预案
4. 建立风险监控指标体系"""

    def focus_category(self) -> str | None:
        return "风险规则"


class ExecutionControlAgent(BaseAgent):
    def __init__(self):
        super().__init__("执行管控Agent", "下发调度任务并跟踪执行状态")

    def system_prompt(self) -> str:
        return """你是执行管控专家。你擅长：
1. 将调度方案拆解为可执行的具体任务
2. 实时跟踪任务执行状态
3. 协调各环节资源
4. 汇总执行结果形成闭环"""

    def focus_category(self) -> str | None:
        return None
