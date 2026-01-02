from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.commands import ReserveProductsCommand, SendNotifyCommand


class IPaymentService(ABC):
    @abstractmethod
    async def charge(self, order_id: UUID):
        raise NotImplementedError

    @abstractmethod
    async def cancel(self, order_id: UUID):
        raise NotImplementedError


class INotificationService(ABC):
    @abstractmethod
    async def notify(self, command: SendNotifyCommand):
        raise NotImplementedError


class IStocksServiceProxy(ABC):
    @abstractmethod
    async def reserve_products(self, command: ReserveProductsCommand):
        raise NotImplementedError
