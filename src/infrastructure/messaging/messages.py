from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field

from src.domain.base import PydanticBase
from src.domain.commands import ExternalReference
from src.domain.entities import Product
from src.domain.enums import CommandTypes, OrderEventTypes


class Message(PydanticBase):
    message_id: UUID = Field(default_factory=uuid4)
    producer: str


class EventMessage(Message):
    action: OrderEventTypes
    external_reference: ExternalReference


class CommandMessage(Message):
    action: CommandTypes
    external_reference: ExternalReference


class OrderMessage(EventMessage):
    order_id: UUID
    aggregate_type: str
    payload: list[Product]


class ProductsPayload(PydanticBase):
    products: list[Product]


class ProductsReservedPayload(ProductsPayload):
    total_price: Decimal


class ProductsReservedMessage(EventMessage):
    action: OrderEventTypes = OrderEventTypes.PRODUCTS_RESERVED
    payload: ProductsReservedPayload


class PaymentChargedMessage(EventMessage):
    action: OrderEventTypes = OrderEventTypes.PAYMENT_CHARGED
    payload: dict[str, Any]


class ProductsCommittedMessage(EventMessage):
    action: OrderEventTypes = OrderEventTypes.PRODUCTS_COMMITTED
    payload: ProductsPayload


class FailedEventPayload(PydanticBase):
    failed_event: OrderEventTypes
    error_message: str


class FailedEventMessage(EventMessage):
    action: OrderEventTypes
    payload: FailedEventPayload
    external_reference: ExternalReference


class CancelOrderMessage(CommandMessage):
    payload: dict[str, Any]
