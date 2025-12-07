from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models import OutboxModel
from src.infrastructure.repositories.base_repository import SQLAlchemyRepository
from src.infrastructure.repositories.interfaces import IOutboxRepository


class OutboxRepository(SQLAlchemyRepository, IOutboxRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, OutboxModel)
