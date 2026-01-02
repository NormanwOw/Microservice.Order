from abc import ABC, abstractmethod

from src.domain.commands import ReserveProductsCommand, SendNotifyCommand


class IPaymentService(ABC): ...


class INotificationService(ABC):
    @abstractmethod
    async def notify(self, command: SendNotifyCommand):
        raise NotImplementedError


class IStocksServiceProxy(ABC):
    @abstractmethod
    async def reserve_products(self, command: ReserveProductsCommand):
        raise NotImplementedError
