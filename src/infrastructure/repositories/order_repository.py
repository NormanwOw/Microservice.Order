from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models import OrderModel
from src.infrastructure.repositories.base_repository import SQLAlchemyRepository
from src.infrastructure.repositories.interfaces import IOrderRepository


class OrderRepository(SQLAlchemyRepository, IOrderRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, OrderModel)
