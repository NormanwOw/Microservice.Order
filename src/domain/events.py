import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from src.domain.base import PydanticBase
from src.domain.entities import Product
from src.domain.enums import CommandTypes, OrderEventTypes, ServiceName
from src.infrastructure.messaging.messages import ProductsPayload


class DomainEvent(PydanticBase):
    pass


class OrderEvent(DomainEvent):
    order_id: UUID | None = None
    payload: dict


class OrderCreated(OrderEvent):
    order_id: UUID = Field(default_factory=uuid.uuid4)
    products: list['Product']
    created_at: datetime = Field(default_factory=datetime.now)
    customer_id: UUID


class PaymentCharged(OrderEvent):
    payload: dict | None = None


class ProductsReserved(OrderEvent):
    pass


class ProductsCommitted(OrderEvent):
    payload: ProductsPayload


class Event(PydanticBase):
    pass


class StepCompleted(Event):
    saga_id: UUID
    service: ServiceName
    command_type: CommandTypes
    command_payload: Optional[dict] = None
    compensation_command_type: Optional[CommandTypes] = None
    compensation_payload: Optional[dict] = None


class StepCompensated(Event):
    saga_id: UUID
    step_name: CommandTypes
    status: OrderEventTypes


class StepFailed(Event):
    pass
