"""订单模型"""
import datetime
from decimal import Decimal
from sqlalchemy import String, Integer, DateTime, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Order(Base):
    __tablename__ = "biz_order"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    order_type: Mapped[str] = mapped_column(String(32), default="SALE")
    status: Mapped[str] = mapped_column(String(16), default="PENDING", index=True)
    customer_name: Mapped[str | None] = mapped_column(String(128))
    product_name: Mapped[str | None] = mapped_column(String(128))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    total_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    warehouse_name: Mapped[str | None] = mapped_column(String(128))
    shipping_address: Mapped[str | None] = mapped_column(Text)
    required_date: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    shipped_date: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_date: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    remark: Mapped[str | None] = mapped_column(String(256))
    created_by: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
