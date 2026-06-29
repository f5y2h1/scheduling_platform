"""
履约 Repository
"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fulfillment import Fulfillment
from app.repositories.base_repository import BaseRepository


class FulfillmentRepository(BaseRepository[Fulfillment]):
    def __init__(self, db: AsyncSession):
        super().__init__(Fulfillment, db)

    async def get_by_fulfillment_no(self, fulfillment_no: str) -> Fulfillment | None:
        return await self.get_by(fulfillment_no=fulfillment_no)

    async def get_by_order_no(self, order_no: str) -> list[Fulfillment]:
        query = select(Fulfillment).where(Fulfillment.order_no == order_no)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_by_status(self, status: str, skip: int = 0, limit: int = 100) -> list[Fulfillment]:
        return await self.list(skip=skip, limit=limit, status=status)

    async def get_fulfillment_stats(self) -> dict:
        pending = await self.count(status="PENDING")
        in_transit = await self.count(status="IN_TRANSIT")
        signed = await self.count(status="SIGNED")
        return {
            "pending": pending,
            "in_transit": in_transit,
            "signed": signed,
        }