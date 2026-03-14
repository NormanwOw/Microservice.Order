from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repositories import IProcessedMessagesModelRepository
from src.infrastructure.models import ProcessedMessagesModel
from src.infrastructure.repositories.base_repository import SQLAlchemyRepository


class ProcessedMessagesModelRepository(SQLAlchemyRepository, IProcessedMessagesModelRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, ProcessedMessagesModel)
