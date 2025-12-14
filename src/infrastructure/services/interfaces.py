from abc import ABC, abstractmethod
from uuid import UUID


class IPaymentService(ABC):
    @abstractmethod
    async def verify(self, order_id: UUID):
        raise NotImplementedError

    @abstractmethod
    async def cancel(self, order_id: UUID):
        raise NotImplementedError
