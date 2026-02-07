from abc import ABC, abstractmethod

from src.domain.commands import ChargePaymentCommand, ReserveProductsCommand, SendNotifyCommand
from src.infrastructure.uow.interfaces import IUnitOfWork


class IPaymentService(ABC):
    @abstractmethod
    async def charge_payment(self, uow: IUnitOfWork, command: ChargePaymentCommand):
        raise NotImplementedError


class INotificationService(ABC):
    @abstractmethod
    async def notify(self, uow: IUnitOfWork, command: SendNotifyCommand):
        raise NotImplementedError


class IStocksServiceProxy(ABC):
    @abstractmethod
    async def reserve_products(self, uow: IUnitOfWork, command: ReserveProductsCommand):
        raise NotImplementedError
