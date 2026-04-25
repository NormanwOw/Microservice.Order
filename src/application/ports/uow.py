from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional, Self, Type

from src.application.ports import repositories as i


class IUnitOfWork(ABC):
    @property
    def outbox(self) -> i.IOutboxRepository:
        raise NotImplementedError

    @property
    def processed_messages(self) -> i.IProcessedMessagesModelRepository:
        raise NotImplementedError

    @property
    def orders(self) -> i.IOrderRepository:
        raise NotImplementedError

    @property
    def create_order_saga(self) -> i.ICreateOrderSagaRepository:
        raise NotImplementedError

    @property
    def create_order_saga_step(self) -> i.ICreateOrderSagaStepRepository:
        raise NotImplementedError

    @property
    def order_events(self) -> i.IOrderEventRepository:
        raise NotImplementedError

    async def __aenter__(self) -> Self:
        raise NotImplementedError

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
