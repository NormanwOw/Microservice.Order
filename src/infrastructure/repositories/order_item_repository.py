from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models import OrderItemModel
from src.infrastructure.repositories.base_repository import SQLAlchemyRepository
from src.infrastructure.repositories.interfaces import IOrderItemRepository


class OrderItemRepository(SQLAlchemyRepository, IOrderItemRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, OrderItemModel)
