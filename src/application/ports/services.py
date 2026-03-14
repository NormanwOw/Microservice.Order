from abc import ABC, abstractmethod

from src.application.ports.uow import IUnitOfWork
from src.domain.commands import (
    CancelCommand,
    ChargePaymentCommand,
    CommitProductsCommand,
    ReserveProductsCommand,
    SendSuccessCreatedOrderNotifyCommand,
)


class IPaymentService(ABC):
    @abstractmethod
    async def charge_payment(self, uow: IUnitOfWork, command: ChargePaymentCommand):
        raise NotImplementedError

    @abstractmethod
    async def compensate(self, uow: IUnitOfWork, command: CancelCommand):
        raise NotImplementedError


class INotificationService(ABC):
    @abstractmethod
    async def notify_success_created_order(
        self, uow: IUnitOfWork, command: SendSuccessCreatedOrderNotifyCommand
    ):
        raise NotImplementedError


class IStocksServiceProxy(ABC):
    @abstractmethod
    async def reserve_products(self, uow: IUnitOfWork, command: ReserveProductsCommand):
        raise NotImplementedError

    @abstractmethod
    async def commit_products(self, uow: IUnitOfWork, command: CommitProductsCommand):
        raise NotImplementedError

    @abstractmethod
    async def compensate(self, uow: IUnitOfWork, command: CancelCommand):
        raise NotImplementedError


class IOrderServiceProxy(ABC):
    @abstractmethod
    async def compensate(self, uow: IUnitOfWork, command: CancelCommand):
        raise NotImplementedError
