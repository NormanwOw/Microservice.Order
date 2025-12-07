from abc import ABC, abstractmethod
from typing import Any, TypeVar

from sqlalchemy.orm import InstrumentedAttribute

from src.infrastructure.models import Base

T = TypeVar("T", bound=Base)


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


class ICreateOrderSagaRepository(ISQLAlchemyRepository, ABC): ...


class ICreateOrderSagaStepRepository(ISQLAlchemyRepository, ABC): ...
