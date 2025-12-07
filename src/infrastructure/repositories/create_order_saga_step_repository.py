from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models import CreateOrderSagaStepModel
from src.infrastructure.repositories.base_repository import SQLAlchemyRepository
from src.infrastructure.repositories.interfaces import ICreateOrderSagaStepRepository


class CreateOrderSagaStepRepository(
    SQLAlchemyRepository, ICreateOrderSagaStepRepository
):
    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, CreateOrderSagaStepModel)
