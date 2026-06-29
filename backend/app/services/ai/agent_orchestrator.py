"""
Agent 编排引擎
单Agent/流水线/并行 三种模式
"""
import asyncio

from app.core.config import settings
from app.core.logger import logger
from app.services.ai.agents import (
    DemandForecastAgent, InventoryOptimizationAgent,
    SchedulingDecisionAgent, CostOptimizationAgent,
    RiskControlAgent, ExecutionControlAgent,
    BaseAgent,
)
from app.services.ai.bailian_client import bailian_client
from app.services.rag.knowledge_base import kb_service


class AgentOrchestrator:
    """Agent 编排器"""

    def __init__(self):
        self.agents: dict[str, BaseAgent] = {
            "demand_forecast": DemandForecastAgent(),
            "inventory_optimization": InventoryOptimizationAgent(),
            "scheduling_decision": SchedulingDecisionAgent(),
            "cost_optimization": CostOptimizationAgent(),
            "risk_control": RiskControlAgent(),
            "execution_control": ExecutionControlAgent(),
        }

    def get_models(self) -> list[dict]:
        return bailian_client.get_models()

    def get_agents(self) -> list[dict]:
        return [
            {"id": k, "name": a.name, "description": a.description,
             "category": a.focus_category() or "通用"}
            for k, a in self.agents.items()
        ]

    async def invoke_agent(self, agent_id: str, model: str | None, query: str) -> dict:
        """单Agent调用"""
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"未知Agent: {agent_id}")
        result = await agent.think(query, model=model)
        return {"agent_id": agent_id, "model": model or "default", "query": query, "result": result}

    async def run_pipeline(self, model: str | None, initial_query: str) -> dict:
        """全流程流水线"""
        logger.info(f"启动流水线, model={model}")
        results = {}

        # Step 1
        f = await self.agents["demand_forecast"].think(initial_query, model=model)
        results["demand_forecast"] = f

        # Step 2
        inv = await self.agents["inventory_optimization"].think(
            f"基于需求预测结果给出库存优化建议:\n{f}", model=model)
        results["inventory_optimization"] = inv

        # Step 3
        sch = await self.agents["scheduling_decision"].think(
            f"基于库存方案制定调度计划:\n{inv}", model=model)
        results["scheduling_decision"] = sch

        # Step 4
        cost = await self.agents["cost_optimization"].think(
            f"核算调度方案成本:\n{sch}", model=model)
        results["cost_optimization"] = cost

        # Step 5
        risk = await self.agents["risk_control"].think(
            f"评估方案风险:\n预测:{f}\n调度:{sch}", model=model)
        results["risk_control"] = risk

        # Step 6
        exe = await self.agents["execution_control"].think(
            f"生成执行计划:\n{sch}\n{cost}", model=model)
        results["execution_control"] = exe

        logger.info("流水线完成")
        return results

    async def invoke_parallel(self, model: str | None, queries: dict[str, str]) -> dict:
        """并行调用"""
        logger.info(f"并行调用 {len(queries)} 个Agent")
        tasks = []
        keys = []
        for agent_id, query in queries.items():
            keys.append(agent_id)
            tasks.append(self.invoke_agent(agent_id, model, query))

        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        results = {}
        for k, r in zip(keys, results_list):
            if isinstance(r, Exception):
                results[k] = {"error": str(r)}
            else:
                results[k] = r
        return results


# 全局单例
orchestrator = AgentOrchestrator()


async def init_knowledge_base():
    """启动时初始化知识库"""
    try:
        await kb_service.init_defaults()
    except Exception as e:
        logger.warning(f"知识库初始化失败（可能Qdrant未启动）: {e}")
