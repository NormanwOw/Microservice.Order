from abc import ABC, abstractmethod
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy.orm import InstrumentedAttribute

from src.infrastructure.messaging.messages import OrderMessage
from src.infrastructure.models import Base, CreateOrderSagaModel, ProductModel

T = TypeVar('T', bound=Base)


class ISQLAlchemyRepository(ABC):
    @abstractmethod
    async def add(self, data: T) -> T:
        raise NotImplementedError

    @abstractmethod
    async def find_all(
        self,
        filter_field: InstrumentedAttribute = None,
        filter_value: Any = None,
        order_by: InstrumentedAttribute = None,
    ) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    async def find_one(
        self, filter_field: InstrumentedAttribute = None, filter_value: Any = None
    ) -> T:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self,
        values: dict,
        filter_field: InstrumentedAttribute = None,
        filter_value: Any = None,
    ):
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, filter_field: InstrumentedAttribute, filter_value: Any):
        raise NotImplementedError

    @abstractmethod
    async def delete(self):
        raise NotImplementedError


class IOutboxRepository(ISQLAlchemyRepository, ABC): ...


class IProcessedMessagesModelRepository(ISQLAlchemyRepository, ABC): ...


class IOrderRepository(ISQLAlchemyRepository, ABC): ...


class IOrderItemRepository(ISQLAlchemyRepository, ABC): ...


class ICreateOrderSagaRepository(ISQLAlchemyRepository, ABC):
    @abstractmethod
    async def create(self, message: OrderMessage):
        raise NotImplementedError

    @abstractmethod
    async def get_by_order_id(self, order_id: UUID) -> CreateOrderSagaModel:
        raise NotImplementedError


class ICreateOrderSagaStepRepository(ISQLAlchemyRepository, ABC): ...


class IProductRepository(ISQLAlchemyRepository, ABC):
    @abstractmethod
    async def find_exists_by_ids(self, ids: list[UUID]) -> list[ProductModel]:
        raise NotImplementedError
