import uuid
from datetime import datetime
from uuid import UUID

from pydantic import Field

from src.domain.base import PydanticBase
from src.domain.entities import Product


class DomainEvent(PydanticBase):
    pass


class OrderEvent(DomainEvent):
    order_id: UUID | None = None


class OrderCreated(OrderEvent):
    order_id: UUID = Field(default_factory=uuid.uuid4)
    products: list['Product']
    created_at: datetime = Field(default_factory=datetime.now)
    customer_id: UUID


class OrderPayed(OrderEvent):
    pass


class PaymentCharged(OrderEvent):
    pass


class FailedCreateOrder(OrderEvent):
    pass
