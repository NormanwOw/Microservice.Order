from abc import ABC, abstractmethod
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy.orm import InstrumentedAttribute

from src.domain.aggregates import Order
from src.domain.events import Event
from src.infrastructure.models import Base, OrderEventModel

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


class IOrderRepository(ISQLAlchemyRepository, ABC):
    @abstractmethod
    async def load(self, order_id: UUID) -> Order | None:
        raise NotImplementedError

    @abstractmethod
    async def append_events(self, order_id: UUID, expected_version: int, events: list[Event]):
        raise NotImplementedError

    @abstractmethod
    async def upsert_projection(self, order: Order, customer_id: UUID):
        raise NotImplementedError


class IOrderEventRepository(ISQLAlchemyRepository, ABC):
    @abstractmethod
    async def load_stream(self, order_id: UUID) -> list[OrderEventModel]:
        raise NotImplementedError


class ICreateOrderSagaRepository(ISQLAlchemyRepository, ABC):
    @abstractmethod
    async def start(self, saga_id: UUID, order: Order, customer_id: UUID):
        raise NotImplementedError


class ICreateOrderSagaStepRepository(ISQLAlchemyRepository, ABC): ...
