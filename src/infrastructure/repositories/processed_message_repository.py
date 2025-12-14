from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models import ProcessedMessagesModel
from src.infrastructure.repositories.base_repository import SQLAlchemyRepository
from src.infrastructure.repositories.interfaces import IProcessedMessagesModelRepository


class ProcessedMessagesModelRepository(
    SQLAlchemyRepository, IProcessedMessagesModelRepository
):
    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, ProcessedMessagesModel)
