"""
供应商 Repository
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplier import Supplier
from app.repositories.base_repository import BaseRepository


class SupplierRepository(BaseRepository[Supplier]):
    def __init__(self, db: AsyncSession):
        super().__init__(Supplier, db)

    async def get_by_code(self, code: str) -> Supplier | None:
        return await self.get_by(code=code)

    async def list_active(self, skip: int = 0, limit: int = 100) -> list[Supplier]:
        return await self.list(skip=skip, limit=limit, status="ACTIVE")

    async def search(self, keyword: str, skip: int = 0, limit: int = 100) -> list[Supplier]:
        query = (
            select(Supplier)
            .where(
                (Supplier.name.ilike(f"%{keyword}%"))
                | (Supplier.code.ilike(f"%{keyword}%"))
                | (Supplier.contact_name.ilike(f"%{keyword}%"))
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()