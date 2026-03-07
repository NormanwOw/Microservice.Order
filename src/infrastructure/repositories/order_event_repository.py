from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repositories import IOrderEventRepository
from src.infrastructure.models import OrderEventModel
from src.infrastructure.repositories.base_repository import SQLAlchemyRepository


class OrderEventRepository(SQLAlchemyRepository, IOrderEventRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, OrderEventModel)
