from abc import ABC, abstractmethod

from src.application.ports.uow import IUnitOfWork
from src.domain.commands import (
    CancelCommand,
    ChargePaymentCommand,
    CommitProductsCommand,
    NotifyCommand,
    ReserveProductsCommand,
)


class BaseService(ABC):
    async def compensate(self, uow: IUnitOfWork, command: CancelCommand) -> None:
        raise NotImplementedError


class IPaymentService(BaseService):
    @abstractmethod
    async def charge_payment(self, uow: IUnitOfWork, command: ChargePaymentCommand) -> None:
        raise NotImplementedError


class INotificationService(BaseService):
    @abstractmethod
    async def notify(self, uow: IUnitOfWork, command: NotifyCommand) -> None:
        raise NotImplementedError


class IStocksServiceProxy(BaseService):
    @abstractmethod
    async def reserve_products(self, uow: IUnitOfWork, command: ReserveProductsCommand) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit_products(self, uow: IUnitOfWork, command: CommitProductsCommand) -> None:
        raise NotImplementedError


class IOrderServiceProxy(BaseService): ...
