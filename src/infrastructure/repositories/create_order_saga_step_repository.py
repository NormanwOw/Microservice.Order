from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repositories import ICreateOrderSagaStepRepository
from src.infrastructure.models import CreateOrderSagaStepModel
from src.infrastructure.repositories.base_repository import SQLAlchemyRepository


class CreateOrderSagaStepRepository(SQLAlchemyRepository, ICreateOrderSagaStepRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, CreateOrderSagaStepModel)
