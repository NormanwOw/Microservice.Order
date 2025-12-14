from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models import ProductModel
from src.infrastructure.repositories.base_repository import SQLAlchemyRepository
from src.infrastructure.repositories.interfaces import IProductRepository


class ProductRepository(SQLAlchemyRepository, IProductRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, ProductModel)

    async def find_exists_by_ids(self, ids: list[UUID]) -> list[ProductModel]:
        res = await self.__session.scalars(
            select(ProductModel)
            .where(ProductModel.id.in_(ids), ProductModel.stocks > 0)
            .with_for_update()
        )
        return list(res.all())
