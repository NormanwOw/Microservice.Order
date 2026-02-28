from abc import ABC, abstractmethod

from src.domain.commands import (
    ChargePaymentCommand,
    CommitProductsCommand,
    ReserveProductsCommand,
    SendSuccessCreatedOrderNotifyCommand,
)
from src.infrastructure.uow.interfaces import IUnitOfWork


class IPaymentService(ABC):
    @abstractmethod
    async def charge_payment(self, uow: IUnitOfWork, command: ChargePaymentCommand):
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
