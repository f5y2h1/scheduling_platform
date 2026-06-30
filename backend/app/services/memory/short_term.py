"""
Short-Term Memory: ContextManager + Redis + PostgreSQL
管理多轮会话上下文，实现上下文窗口控制与 Session 隔离

Architecture:
- Redis: 热数据缓存（最近 N 轮对话），带 TTL 过期
- PostgreSQL: 全量消息持久化，支持历史回溯
- ContextManager: 上下文构建、摘要压缩、窗口滑动
"""
import json
import time
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta

from app.core.config import settings
from app.core.logger import logger
from app.services.memory.models import ChatSession, ChatMessage


class ShortTermMemory:
    """
    短期记忆管理器
    - Redis 作为一级缓存（热数据，快速读写）
    - PostgreSQL 作为二级存储（全量持久化）
    - 自动上下文窗口管理 + 摘要压缩
    """

    # 上下文窗口配置
    MAX_HISTORY_ROUNDS = 10       # 最大保留轮数
    MAX_CONTEXT_TOKENS = 4000     # 上下文 token 上限
    COMPRESS_THRESHOLD = 5        # 超过此轮数触发摘要
    REDIS_TTL_SECONDS = 3600 * 24  # Redis 缓存 24 小时

    def __init__(self, redis_client=None, session_factory=None):
        self._redis = redis_client
        self._session_factory = session_factory
        self._redis_available = False

    async def initialize(self):
        """异步初始化，检测 Redis 可用性"""
        if self._redis is not None:
            try:
                await self._redis.ping()
                self._redis_available = True
                logger.info("[短期记忆] Redis 连接成功，启用缓存加速")
            except Exception as e:
                logger.warning(f"[短期记忆] Redis 不可用，仅使用 PostgreSQL: {e}")
                self._redis_available = False
        else:
            logger.info("[短期记忆] 未配置 Redis，使用 PostgreSQL 模式")

    # ==================== 消息管理 ====================

    async def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """获取会话历史消息（优先 Redis，回退 PostgreSQL）"""
        # 1. 尝试从 Redis 读取热数据
        if self._redis_available:
            try:
                cached = await self._redis.get(f"chat:history:{session_id}")
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"[短期记忆] Redis 读取失败: {e}")

        # 2. 从 PostgreSQL 读取全量数据
        return await self._load_from_db(session_id)

    async def add_message(self, session_id: str, role: str, content: str,
                          image: str = None, tool_calls: List = None,
                          user_id: int = None) -> Dict[str, Any]:
        """添加消息到会话历史"""
        message = {
            "role": role,
            "content": content,
            "image": image,
            "tool_calls": tool_calls,
            "timestamp": time.time(),
        }

        # 1. 写入 PostgreSQL
        await self._save_to_db(session_id, role, content, image, tool_calls, user_id)

        # 2. 更新 Redis 缓存
        history = await self.get_history(session_id)
        history.append(message)
        history = self._compress_history(session_id, history)

        if self._redis_available:
            try:
                await self._redis.setex(
                    f"chat:history:{session_id}",
                    self.REDIS_TTL_SECONDS,
                    json.dumps(history, ensure_ascii=False)
                )
            except Exception as e:
                logger.warning(f"[短期记忆] Redis 写入失败: {e}")

        return message

    async def clear_history(self, session_id: str):
        """清除会话历史"""
        # 软删除 PostgreSQL 中的会话
        try:
            async with self._session_factory() as db:
                from sqlalchemy import select, update
                await db.execute(
                    update(ChatSession)
                    .where(ChatSession.session_id == session_id)
                    .values(is_active=False, updated_at=datetime.now(timezone.utc))
                )
                await db.commit()
        except Exception as e:
            logger.error(f"[短期记忆] 清除会话失败: {e}")

        # 清除 Redis 缓存
        if self._redis_available:
            try:
                await self._redis.delete(f"chat:history:{session_id}")
            except Exception:
                pass

    # ==================== 上下文构建 ====================

    def build_context_messages(self, session_id: str, current_query: str,
                               image: str = None) -> List[Dict[str, Any]]:
        """
        构建发给 LLM 的完整消息上下文
        包含系统提示词 + 历史消息 + 当前查询
        """
        # 注意：这是同步方法，需要调用者先 await get_history 再传入
        messages = [{
            "role": "system",
            "content": self._get_system_prompt()
        }]
        return messages

    def _get_system_prompt(self) -> str:
        return (
            "你是 Xuni 供应链智能调度平台的 AI 助手，具备以下能力：\n"
            "1. **供应链管理**：需求预测、库存优化、调度决策、成本分析、风险控制\n"
            "2. **工具调用**：可查询库存、订单、供应商等真实业务数据\n"
            "3. **图片理解**：可分析供应链相关图片（流程图、物流单据、库存照片等）\n"
            "4. **知识检索**：可检索企业内部知识库获取专业信息\n"
            "5. **多模态交互**：支持文本、语音（转文字）、图片输入\n\n"
            "请根据用户需求提供准确、专业的供应链管理建议。"
        )

    def _compress_history(self, session_id: str,
                          history: List[Dict]) -> List[Dict]:
        """滑动窗口压缩 - 保留最近 N 轮 + 生成摘要"""
        if len(history) <= self.MAX_HISTORY_ROUNDS:
            return history

        compressed = []
        if len(history) > self.COMPRESS_THRESHOLD:
            old_messages = history[:-self.COMPRESS_THRESHOLD]
            summary = self._summarize_messages(old_messages)
            compressed.append({
                "role": "system",
                "content": f"【对话摘要】{summary}",
                "is_summary": True,
                "timestamp": time.time(),
            })

        compressed.extend(history[-self.COMPRESS_THRESHOLD:])
        return compressed

    def _summarize_messages(self, messages: List[Dict]) -> str:
        """生成对话摘要（简单版本，可升级为 LLM 摘要）"""
        user_msgs = [m["content"] for m in messages if m["role"] == "user"]
        assistant_msgs = [m["content"] for m in messages
                          if m["role"] == "assistant"]

        topics = []
        for msg in user_msgs:
            # 提取关键词
            for kw in ["库存", "订单", "调度", "供应商", "成本", "风险",
                        "入库", "出库", "预测", "优化"]:
                if kw in msg and kw not in topics:
                    topics.append(kw)

        return (f"用户发起了 {len(user_msgs)} 轮对话，"
                f"涉及主题：{'、'.join(topics[:5]) if topics else '通用咨询'}，"
                f"助手已完成 {len(assistant_msgs)} 次回复")

    async def generate_llm_summary(self, session_id: str) -> str:
        """使用 LLM 生成高质量对话摘要（异步）"""
        history = await self.get_history(session_id)
        if not history:
            return ""

        user_content = "\n".join(
            [m["content"][:200] for m in history if m["role"] == "user"]
        )
        assistant_content = "\n".join(
            [m["content"][:200] for m in history if m["role"] == "assistant"]
        )

        try:
            from app.services.ai.bailian_client import bailian_client
            summary = bailian_client.simple_chat(
                system_prompt="你是对话摘要助手，请用简洁中文概括对话要点（50字以内）。",
                user_message=f"用户:\n{user_content[:500]}\n\n助手:\n{assistant_content[:500]}\n\n摘要：",
            )
            return summary[:200] if summary else self._summarize_messages(history)
        except Exception as e:
            logger.warning(f"[短期记忆] LLM 摘要生成失败: {e}")
            return self._summarize_messages(history)

    # ==================== 会话管理 ====================

    async def list_sessions(self, user_id: int = None) -> List[Dict]:
        """列出所有活跃会话"""
        try:
            async with self._session_factory() as db:
                from sqlalchemy import select
                query = select(ChatSession).where(
                    ChatSession.is_active == True
                ).order_by(ChatSession.updated_at.desc())
                result = await db.execute(query)
                sessions = result.scalars().all()
                return [{
                    "session_id": s.session_id,
                    "title": s.title,
                    "message_count": s.message_count,
                    "summary": s.summary,
                    "created_at": str(s.created_at),
                    "updated_at": str(s.updated_at),
                } for s in sessions]
        except Exception as e:
            logger.error(f"[短期记忆] 获取会话列表失败: {e}")
            return []

    async def get_session_detail(self, session_id: str) -> Optional[Dict]:
        """获取会话详情"""
        history = await self.get_history(session_id)
        summary = await self.generate_llm_summary(session_id)

        try:
            async with self._session_factory() as db:
                from sqlalchemy import select
                result = await db.execute(
                    select(ChatSession).where(
                        ChatSession.session_id == session_id
                    )
                )
                session = result.scalar_one_or_none()
                if session:
                    return {
                        "session_id": session.session_id,
                        "title": session.title,
                        "message_count": session.message_count,
                        "summary": summary,
                        "messages": history,
                        "created_at": str(session.created_at),
                        "updated_at": str(session.updated_at),
                    }
        except Exception as e:
            logger.error(f"[短期记忆] 获取会话详情失败: {e}")

        return {
            "session_id": session_id,
            "title": "历史会话",
            "message_count": len(history),
            "summary": summary,
            "messages": history,
        }

    async def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        try:
            async with self._session_factory() as db:
                from sqlalchemy import delete
                await db.execute(
                    delete(ChatMessage).where(
                        ChatMessage.session_id_fk == session_id
                    )
                )
                await db.execute(
                    delete(ChatSession).where(
                        ChatSession.session_id == session_id
                    )
                )
                await db.commit()
        except Exception as e:
            logger.error(f"[短期记忆] 删除会话失败: {e}")
            return False

        if self._redis_available:
            try:
                await self._redis.delete(f"chat:history:{session_id}")
            except Exception:
                pass

        return True

    # ==================== 内部方法 ====================

    async def _load_from_db(self, session_id: str) -> List[Dict]:
        """从 PostgreSQL 加载会话消息"""
        try:
            async with self._session_factory() as db:
                from sqlalchemy import select
                result = await db.execute(
                    select(ChatMessage)
                    .where(ChatMessage.session_id_fk == session_id)
                    .order_by(ChatMessage.created_at.asc())
                    .limit(200)
                )
                messages = result.scalars().all()
                return [{
                    "role": m.role,
                    "content": m.content,
                    "image": m.image_url,
                    "tool_calls": m.tool_calls,
                    "timestamp": m.created_at.timestamp() if m.created_at else time.time(),
                } for m in messages]
        except Exception as e:
            logger.error(f"[短期记忆] DB 加载失败: {e}")
            return []

    async def _save_to_db(self, session_id: str, role: str, content: str,
                          image: str = None, tool_calls: List = None,
                          user_id: int = None):
        """持久化消息到 PostgreSQL"""
        try:
            async with self._session_factory() as db:
                from sqlalchemy import select, update

                # 确保 Session 记录存在
                result = await db.execute(
                    select(ChatSession).where(
                        ChatSession.session_id == session_id
                    )
                )
                session = result.scalar_one_or_none()

                if not session:
                    title = content[:30] if role == "user" and content else "新对话"
                    session = ChatSession(
                        session_id=session_id,
                        user_id=user_id,
                        title=title,
                        message_count=0,
                    )
                    db.add(session)
                    await db.flush()
                else:
                    # 更新 message_count
                    await db.execute(
                        update(ChatSession)
                        .where(ChatSession.session_id == session_id)
                        .values(
                            message_count=ChatSession.message_count + 1,
                            updated_at=datetime.now(timezone.utc)
                        )
                    )

                # 保存消息
                message = ChatMessage(
                    session_id_fk=session_id,
                    role=role,
                    content=content,
                    image_url=image,
                    tool_calls=tool_calls,
                    token_count=len(content) // 2 if content else 0,
                )
                db.add(message)
                await db.commit()
        except Exception as e:
            logger.error(f"[短期记忆] DB 保存失败: {e}")

    async def update_session_title(self, session_id: str, title: str):
        """更新会话标题"""
        try:
            async with self._session_factory() as db:
                from sqlalchemy import update
                await db.execute(
                    update(ChatSession)
                    .where(ChatSession.session_id == session_id)
                    .values(title=title, updated_at=datetime.now(timezone.utc))
                )
                await db.commit()
        except Exception as e:
            logger.error(f"[短期记忆] 更新标题失败: {e}")
