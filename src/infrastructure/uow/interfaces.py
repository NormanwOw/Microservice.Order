from abc import ABC, abstractmethod

from src.infrastructure.repositories import interfaces as i


class IUnitOfWork(ABC):
    outbox: i.IOutboxRepository
    processed_messages: i.IProcessedMessagesModelRepository
    orders: i.IOrderRepository
    create_order_saga: i.ICreateOrderSagaRepository
    create_order_saga_step: i.ICreateOrderSagaStepRepository

    async def __aenter__(self):
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError
