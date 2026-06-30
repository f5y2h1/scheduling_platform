"""
Long-Term Memory: PostgreSQL (profiles/preferences) + Qdrant (semantic search)
存储用户画像、业务偏好、历史经验，实现个性化推荐与历史经验复用

Architecture:
- PostgreSQL: 用户偏好、Agent 执行记录（结构化查询）
- Qdrant: 语义可检索的历史经验、决策记录（向量检索）
"""
import json
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from app.core.config import settings
from app.core.logger import logger
from app.services.memory.models import UserPreference, AgentExecutionRecord


class LongTermMemory:
    """
    长期记忆管理器
    - 用户画像与偏好管理
    - Agent 执行经验积累与检索
    - 历史决策语义搜索
    """

    def __init__(self, session_factory=None, qdrant_store=None, embedding_client=None):
        self._session_factory = session_factory
        self._qdrant = qdrant_store
        self._embedding = embedding_client

    # ==================== 用户画像 ====================

    async def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """获取用户偏好设置"""
        try:
            async with self._session_factory() as db:
                from sqlalchemy import select
                result = await db.execute(
                    select(UserPreference).where(
                        UserPreference.user_id == user_id
                    )
                )
                pref = result.scalar_one_or_none()
                if pref:
                    return {
                        "user_id": pref.user_id,
                        "preferred_model": pref.preferred_model,
                        "language": pref.language,
                        "notification_enabled": pref.notification_enabled,
                        "theme": pref.theme,
                        "business_focus": pref.business_focus or [],
                        "custom_settings": pref.custom_settings or {},
                    }
        except Exception as e:
            logger.error(f"[长期记忆] 获取偏好失败: {e}")
        return self._default_preferences(user_id)

    async def save_user_preferences(self, user_id: int,
                                     preferences: Dict[str, Any]) -> bool:
        """保存用户偏好"""
        try:
            async with self._session_factory() as db:
                from sqlalchemy import select
                result = await db.execute(
                    select(UserPreference).where(
                        UserPreference.user_id == user_id
                    )
                )
                pref = result.scalar_one_or_none()

                if pref:
                    for key, value in preferences.items():
                        if hasattr(pref, key):
                            setattr(pref, key, value)
                else:
                    pref = UserPreference(user_id=user_id, **preferences)
                    db.add(pref)

                pref.updated_at = datetime.now(timezone.utc)
                await db.commit()
                logger.info(f"[长期记忆] 用户偏好已保存: user_id={user_id}")
                return True
        except Exception as e:
            logger.error(f"[长期记忆] 保存偏好失败: {e}")
            return False

    def _default_preferences(self, user_id: int) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "preferred_model": "qwen3.5-omni-plus",
            "language": "zh-CN",
            "notification_enabled": True,
            "theme": "light",
            "business_focus": ["库存管理", "订单管理", "调度决策"],
            "custom_settings": {},
        }

    # ==================== Agent 执行经验 ====================

    async def record_execution(self, session_id: str, agent_name: str,
                                query: str, result: str, success: bool = True,
                                duration_ms: float = 0,
                                tool_calls_count: int = 0,
                                iteration_count: int = 1,
                                metadata: Dict = None) -> str:
        """记录 Agent 执行经验"""
        record_id = f"EXP-{hashlib.md5(f'{session_id}{agent_name}{datetime.now().isoformat()}'.encode()).hexdigest()[:12]}"

        # 1. 持久化到 PostgreSQL
        try:
            async with self._session_factory() as db:
                record = AgentExecutionRecord(
                    session_id=session_id,
                    agent_name=agent_name,
                    query=query,
                    result=result[:2000] if result else "",
                    success=success,
                    duration_ms=duration_ms,
                    tool_calls_count=tool_calls_count,
                    iteration_count=iteration_count,
                    metadata_json=metadata,
                )
                db.add(record)
                await db.commit()
        except Exception as e:
            logger.error(f"[长期记忆] 记录执行经验失败: {e}")

        # 2. 向量化存储到 Qdrant（用于语义检索）
        await self._index_to_qdrant(record_id, agent_name, query, result,
                                     success, metadata)

        return record_id

    async def recall_similar_experiences(self, query: str,
                                          top_k: int = 5) -> List[Dict]:
        """检索相似的历史经验（语义搜索）"""
        if not self._qdrant or not self._embedding:
            return []

        try:
            vector = self._embedding.embed(query)
            if not vector:
                return []

            results = self._qdrant.search(
                collection=settings.DECISION_COLLECTION,
                query_vector=vector,
                top_k=top_k,
                score_threshold=0.65,
            )

            experiences = []
            for r in results:
                payload = r.get("payload", {})
                experiences.append({
                    "id": r["id"],
                    "score": round(r["score"], 3),
                    "agent_name": payload.get("agent_name", ""),
                    "query": payload.get("query", ""),
                    "result_summary": (payload.get("result", "") or "")[:300],
                    "success": payload.get("success", True),
                    "recorded_at": payload.get("recorded_at", ""),
                })

            return experiences
        except Exception as e:
            logger.warning(f"[长期记忆] 经验检索失败: {e}")
            return []

    async def _index_to_qdrant(self, record_id: str, agent_name: str,
                                query: str, result: str, success: bool,
                                metadata: Dict = None):
        """将执行经验索引到 Qdrant"""
        if not self._qdrant or not self._embedding:
            return

        try:
            text = f"Agent: {agent_name}\nQuery: {query}\nResult: {(result or '')[:500]}"
            vector = self._embedding.embed(text)
            if not vector:
                return

            self._qdrant.upsert(
                collection=settings.DECISION_COLLECTION,
                point_id=record_id,
                vector=vector,
                payload={
                    "agent_name": agent_name,
                    "query": query,
                    "result": (result or "")[:1000],
                    "success": success,
                    "recorded_at": datetime.now(timezone.utc).isoformat(),
                    **(metadata or {}),
                },
            )
        except Exception as e:
            logger.warning(f"[长期记忆] 索引到 Qdrant 失败: {e}")

    # ==================== 个性化推荐 ====================

    async def get_recommended_actions(self, user_id: int,
                                       current_query: str) -> Dict[str, Any]:
        """基于用户画像和历史经验提供个性化推荐"""
        preferences = await self.get_user_preferences(user_id)
        experiences = await self.recall_similar_experiences(current_query, top_k=3)

        recommendations = {
            "preferred_model": preferences.get("preferred_model"),
            "business_focus": preferences.get("business_focus", []),
            "similar_experiences": experiences,
            "suggested_agents": self._suggest_agents(current_query, experiences),
        }

        return recommendations

    def _suggest_agents(self, query: str,
                         experiences: List[Dict]) -> List[str]:
        """根据查询和历史经验推荐合适的 Agent"""
        suggestions = []
        agent_keywords = {
            "需求预测": ["预测", "需求", "趋势", "销量"],
            "库存优化": ["库存", "补货", "缺货", "入库", "出库"],
            "调度决策": ["调度", "运输", "调货", "配送"],
            "成本优化": ["成本", "费用", "价格", "预算"],
            "风险控制": ["风险", "预警", "异常", "安全"],
            "执行管控": ["执行", "跟踪", "状态", "进度"],
        }

        for agent, keywords in agent_keywords.items():
            if any(kw in query for kw in keywords):
                suggestions.append(agent)

        # 从历史经验中提取
        for exp in experiences:
            agent_name = exp.get("agent_name", "")
            if agent_name not in suggestions:
                suggestions.append(agent_name)

        return suggestions[:3] if suggestions else ["需求预测"]

    # ==================== 统计与画像分析 ====================

    async def get_execution_stats(self, user_id: int = None) -> Dict[str, Any]:
        """获取执行统计信息"""
        try:
            async with self._session_factory() as db:
                from sqlalchemy import select, func
                query = select(
                    func.count(AgentExecutionRecord.id).label("total"),
                    func.sum(
                        func.case((AgentExecutionRecord.success == True, 1), else_=0)
                    ).label("success_count"),
                    func.avg(AgentExecutionRecord.duration_ms).label("avg_duration"),
                    func.avg(AgentExecutionRecord.iteration_count).label("avg_iterations"),
                )
                result = await db.execute(query)
                row = result.one()
                return {
                    "total_executions": row.total or 0,
                    "success_count": row.success_count or 0,
                    "success_rate": round(
                        (row.success_count or 0) / max(row.total or 1, 1), 2
                    ),
                    "avg_duration_ms": round(row.avg_duration or 0, 1),
                    "avg_iterations": round(row.avg_iterations or 1, 1),
                }
        except Exception as e:
            logger.error(f"[长期记忆] 获取统计失败: {e}")
            return {"total_executions": 0}
