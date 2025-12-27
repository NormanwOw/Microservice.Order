from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models import CustomerModel
from src.infrastructure.repositories.base_repository import SQLAlchemyRepository
from src.infrastructure.repositories.interfaces import ICustomerRepository


class CustomerRepository(SQLAlchemyRepository, ICustomerRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, CustomerModel)
