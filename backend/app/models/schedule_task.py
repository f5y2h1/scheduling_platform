"""调度任务模型"""
import datetime
from sqlalchemy import String, Integer, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class ScheduleTask(Base):
    __tablename__ = "biz_schedule_task"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    task_type: Mapped[str] = mapped_column(String(32), default="DISPATCH")
    status: Mapped[str] = mapped_column(String(16), default="PENDING", index=True)
    order_no: Mapped[str | None] = mapped_column(String(32))
    from_warehouse_name: Mapped[str | None] = mapped_column(String(128))
    to_warehouse_name: Mapped[str | None] = mapped_column(String(128))
    product_name: Mapped[str | None] = mapped_column(String(128))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    ai_suggestion: Mapped[str | None] = mapped_column(Text)
    ai_model_used: Mapped[str | None] = mapped_column(String(32))
    approved_by: Mapped[str | None] = mapped_column(String(64))
    approved_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    remark: Mapped[str | None] = mapped_column(String(256))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
