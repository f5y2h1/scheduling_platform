"""
Memory-related SQLAlchemy Models
用于短期记忆持久化和长期记忆存储
"""
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class ChatSession(Base):
    """聊天会话记录 - 短期记忆持久化"""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    title = Column(String(200), default="新对话")
    message_count = Column(Integer, default=0)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc),
                        onupdate=datetime.datetime.now(datetime.timezone.utc))
    is_active = Column(Boolean, default=True)

    messages = relationship("ChatMessage", back_populates="session",
                            cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    """聊天消息记录"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id_fk = Column(String(64), ForeignKey("chat_sessions.session_id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user / assistant / system / tool
    content = Column(Text, default="")
    image_url = Column(Text, nullable=True)
    tool_calls = Column(JSON, nullable=True)
    token_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    session = relationship("ChatSession", back_populates="messages")


class UserPreference(Base):
    """用户偏好与画像 - 长期记忆"""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    preferred_model = Column(String(50), default="qwen3.5-omni-plus")
    language = Column(String(10), default="zh-CN")
    notification_enabled = Column(Boolean, default=True)
    theme = Column(String(20), default="light")
    business_focus = Column(JSON, nullable=True)  # 关注的业务领域
    custom_settings = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc),
                        onupdate=datetime.datetime.now(datetime.timezone.utc))


class AgentExecutionRecord(Base):
    """Agent 执行记录 - 长期记忆经验积累"""
    __tablename__ = "agent_execution_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False)
    query = Column(Text, nullable=False)
    result = Column(Text, nullable=True)
    success = Column(Boolean, default=True)
    duration_ms = Column(Float, default=0)
    tool_calls_count = Column(Integer, default=0)
    iteration_count = Column(Integer, default=1)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
