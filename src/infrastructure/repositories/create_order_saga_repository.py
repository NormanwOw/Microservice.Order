from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models import CreateOrderSagaModel
from src.infrastructure.repositories.base_repository import SQLAlchemyRepository
from src.infrastructure.repositories.interfaces import ICreateOrderSagaRepository


class CreateOrderSagaRepository(SQLAlchemyRepository, ICreateOrderSagaRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, CreateOrderSagaModel)
