"""
订单 Repository
"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: AsyncSession):
        super().__init__(Order, db)

    async def get_by_order_no(self, order_no: str) -> Order | None:
        return await self.get_by(order_no=order_no)

    async def list_by_status(self, status: str, skip: int = 0, limit: int = 100) -> list[Order]:
        return await self.list(skip=skip, limit=limit, status=status)

    async def count_by_status(self, status: str) -> int:
        return await self.count(status=status)

    async def search(self, keyword: str, skip: int = 0, limit: int = 100) -> list[Order]:
        query = (
            select(Order)
            .where(
                (Order.order_no.ilike(f"%{keyword}%"))
                | (Order.customer_name.ilike(f"%{keyword}%"))
                | (Order.product_name.ilike(f"%{keyword}%"))
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_order_stats(self) -> dict:
        pending = await self.count(status="PENDING")
        processing = await self.count(status="PROCESSING")
        shipped = await self.count(status="SHIPPED")
        delivered = await self.count(status="DELIVERED")
        cancelled = await self.count(status="CANCELLED")

        total_amount = await self.db.execute(
            select(func.coalesce(func.sum(Order.total_amount), 0))
        )

        return {
            "pending": pending,
            "processing": processing,
            "shipped": shipped,
            "delivered": delivered,
            "cancelled": cancelled,
            "total_amount": float(total_amount.scalar_one()),
        }