"""履约模型"""
import datetime
from sqlalchemy import String, Integer, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Fulfillment(Base):
    __tablename__ = "biz_fulfillment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fulfillment_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    order_no: Mapped[str | None] = mapped_column(String(32))
    type: Mapped[str] = mapped_column(String(32), default="DELIVERY")
    status: Mapped[str] = mapped_column(String(16), default="PENDING", index=True)
    carrier_name: Mapped[str | None] = mapped_column(String(128))
    tracking_number: Mapped[str | None] = mapped_column(String(64), index=True)
    warehouse_name: Mapped[str | None] = mapped_column(String(128))
    origin_address: Mapped[str | None] = mapped_column(Text)
    destination_address: Mapped[str | None] = mapped_column(Text)
    logistics_info: Mapped[str | None] = mapped_column(Text)
    estimated_delivery: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    actual_delivery: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    signed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    signed_by: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
