"""
Unified Memory Manager - Three-Tier Architecture

Layer 1 - Working Memory:  LangGraph State + PostgresSaver Checkpointer
Layer 2 - Short-term Memory: Redis + PostgreSQL (context management + session isolation)
Layer 3 - Long-term Memory:  PostgreSQL (profiles) + Qdrant (semantic search)

This is the central memory coordinator for the Xuni Scheduling Platform.
All AI interactions route through this manager for consistent memory handling.
"""
import uuid
from typing import Dict, List, Any, Optional

from app.core.config import settings
from app.core.logger import logger
from app.services.memory.short_term import ShortTermMemory
from app.services.memory.long_term import LongTermMemory


class MemoryManager:
    """
    统一记忆管理器

    三层记忆体系：
    ┌─────────────────────────────────────────────────────────┐
    │ Layer 1: Working Memory (LangGraph State + Checkpointer) │
    │   · 管理 Agent 执行状态                                  │
    │   · PostgresSaver 持久化状态图                           │
    │   · 支持断点续跑                                        │
    ├─────────────────────────────────────────────────────────┤
    │ Layer 2: Short-term Memory (Redis + PostgreSQL)          │
    │   · 多轮对话上下文管理                                   │
    │   · 滑动窗口 + 摘要压缩                                  │
    │   · Session 隔离                                        │
    ├─────────────────────────────────────────────────────────┤
    │ Layer 3: Long-term Memory (PostgreSQL + Qdrant)          │
    │   · 用户画像与偏好                                       │
    │   · 历史经验语义检索                                     │
    │   · 个性化推荐                                          │
    └─────────────────────────────────────────────────────────┘
    """

    def __init__(self):
        self.short_term: Optional[ShortTermMemory] = None
        self.long_term: Optional[LongTermMemory] = None
        self._initialized = False

    async def initialize(self, redis_client=None, session_factory=None,
                         qdrant_store=None, embedding_client=None):
        """异步初始化所有记忆层"""
        if self._initialized:
            return

        # 初始化短期记忆
        self.short_term = ShortTermMemory(
            redis_client=redis_client,
            session_factory=session_factory,
        )
        await self.short_term.initialize()

        # 初始化长期记忆
        self.long_term = LongTermMemory(
            session_factory=session_factory,
            qdrant_store=qdrant_store,
            embedding_client=embedding_client,
        )

        self._initialized = True
        logger.info("[MemoryManager] 三层记忆体系初始化完成")

    # ==================== 短期记忆接口 ====================

    async def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        if not self.short_term:
            return []
        return await self.short_term.get_history(session_id)

    async def add_message(self, session_id: str, role: str, content: str,
                          image: str = None, tool_calls: List = None,
                          user_id: int = None) -> Dict[str, Any]:
        if not self.short_term:
            return {}
        return await self.short_term.add_message(
            session_id, role, content, image, tool_calls, user_id
        )

    async def build_context(self, session_id: str, current_query: str,
                            image: str = None) -> List[Dict[str, Any]]:
        """构建发送给 LLM 的完整上下文"""
        if not self.short_term:
            return [{"role": "user", "content": current_query}]

        history = await self.short_term.get_history(session_id)
        messages = [{
            "role": "system",
            "content": self._system_prompt()
        }]

        # 添加历史消息（已压缩）
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
                "image": msg.get("image"),
            })

        # 添加当前消息
        messages.append({
            "role": "user",
            "content": current_query,
            "image": image,
        })

        return messages

    def _system_prompt(self) -> str:
        return (
            "你是 Xuni 供应链智能调度平台的 AI 助手。你的能力包括：\n"
            "1. **供应链管理**：需求预测、库存优化、调度决策、成本分析、风险控制\n"
            "2. **工具调用**：可调用工具查询库存、订单、供应商等真实业务数据\n"
            "3. **图片理解**：可分析供应链相关图片（流程图、物流单据等）\n"
            "4. **知识检索**：可检索企业内部知识库获取专业信息\n"
            "5. **多模态交互**：支持文本、语音转文字、图片输入\n\n"
            "请提供准确、专业的供应链管理建议。需要数据时请调用工具查询。"
        )

    async def clear_history(self, session_id: str):
        if self.short_term:
            await self.short_term.clear_history(session_id)

    async def list_sessions(self, user_id: int = None) -> List[Dict]:
        if not self.short_term:
            return []
        return await self.short_term.list_sessions(user_id)

    async def get_session(self, session_id: str) -> Optional[Dict]:
        if not self.short_term:
            return None
        return await self.short_term.get_session_detail(session_id)

    async def delete_session(self, session_id: str) -> bool:
        if not self.short_term:
            return False
        return await self.short_term.delete_session(session_id)

    # ==================== 长期记忆接口 ====================

    async def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        if not self.long_term:
            return {}
        return await self.long_term.get_user_preferences(user_id)

    async def save_user_preferences(self, user_id: int,
                                     preferences: Dict[str, Any]) -> bool:
        if not self.long_term:
            return False
        return await self.long_term.save_user_preferences(user_id, preferences)

    async def record_execution(self, session_id: str, agent_name: str,
                                query: str, result: str, **kwargs) -> str:
        """记录 Agent 执行经验（同时写入 DB 和 Qdrant）"""
        if not self.long_term:
            return ""
        return await self.long_term.record_execution(
            session_id, agent_name, query, result, **kwargs
        )

    async def recall_experiences(self, query: str,
                                  top_k: int = 5) -> List[Dict]:
        """语义检索相似历史经验"""
        if not self.long_term:
            return []
        return await self.long_term.recall_similar_experiences(query, top_k)

    async def get_recommendations(self, user_id: int,
                                   query: str) -> Dict[str, Any]:
        """获取个性化推荐"""
        if not self.long_term:
            return {}
        return await self.long_term.get_recommended_actions(user_id, query)

    async def get_execution_stats(self) -> Dict[str, Any]:
        if not self.long_term:
            return {"total_executions": 0}
        return await self.long_term.get_execution_stats()

    # ==================== 工作记忆接口 ====================

    @staticmethod
    async def get_workflow_session(session_id: str) -> Optional[Dict]:
        """获取 LangGraph 工作流会话状态"""
        try:
            from app.services.langgraph.workflow import get_session_history
            return await get_session_history(session_id)
        except Exception as e:
            logger.warning(f"[MemoryManager] 获取工作流会话失败: {e}")
            return None

    @staticmethod
    async def list_workflow_sessions() -> List[Dict]:
        """列出所有工作流会话"""
        try:
            from app.services.langgraph.workflow import list_sessions
            return await list_sessions()
        except Exception as e:
            logger.warning(f"[MemoryManager] 列出工作流会话失败: {e}")
            return []

    # ==================== 综合查询 ====================

    async def get_memory_summary(self, user_id: int = None) -> Dict[str, Any]:
        """获取完整记忆系统概览"""
        workflow_sessions = await self.list_workflow_sessions()
        chat_sessions = await self.list_sessions(user_id)
        stats = await self.get_execution_stats()

        return {
            "working_memory": {
                "active_workflow_sessions": len(workflow_sessions),
                "checkpointer": "PostgreSQL (PostgresSaver)",
            },
            "short_term_memory": {
                "active_chat_sessions": len(chat_sessions),
                "cache_backend": "Redis",
                "persistence": "PostgreSQL",
                "max_history_rounds": ShortTermMemory.MAX_HISTORY_ROUNDS,
            },
            "long_term_memory": {
                "total_executions": stats.get("total_executions", 0),
                "success_rate": stats.get("success_rate", 0),
                "vector_store": "Qdrant",
                "profile_store": "PostgreSQL",
            },
        }


# 全局单例
memory_manager = MemoryManager()
