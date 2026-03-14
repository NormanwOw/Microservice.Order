from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repositories import IOrderEventRepository
from src.infrastructure.models import OrderEventModel
from src.infrastructure.repositories.base_repository import SQLAlchemyRepository


class OrderEventRepository(SQLAlchemyRepository, IOrderEventRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, OrderEventModel)

    async def load_stream(self, order_id: UUID) -> list[OrderEventModel]:
        resp = await self.__session.scalars(
            select(self.model)
            .filter(OrderEventModel.order_id == order_id)
            .order_by(OrderEventModel.created_at)
        )
        return list(resp.all())
