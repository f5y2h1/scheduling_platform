"""
库存 Repository
"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Inventory
from app.repositories.base_repository import BaseRepository


class InventoryRepository(BaseRepository[Inventory]):
    def __init__(self, db: AsyncSession):
        super().__init__(Inventory, db)

    async def get_by_product_and_warehouse(self, product_id: int, warehouse_id: int) -> Inventory | None:
        return await self.get_by(product_id=product_id, warehouse_id=warehouse_id)

    async def list_by_warehouse(self, warehouse_id: int, skip: int = 0, limit: int = 100) -> list[Inventory]:
        return await self.list(skip=skip, limit=limit, warehouse_id=warehouse_id)

    async def list_low_stock(self, threshold: int = 0) -> list[Inventory]:
        query = (
            select(Inventory)
            .where(Inventory.available_quantity <= threshold)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_inventory_stats(self) -> dict:
        total = await self.count()
        low_stock = await self.db.execute(
            select(func.count()).select_from(Inventory).where(Inventory.available_quantity <= Inventory.safety_stock)
        )
        total_quantity = await self.db.execute(
            select(func.coalesce(func.sum(Inventory.quantity), 0))
        )
        return {
            "total_items": total,
            "low_stock_items": low_stock.scalar_one() or 0,
            "total_quantity": int(total_quantity.scalar_one()),
        }