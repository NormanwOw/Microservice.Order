from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import Field

from src.domain.base import PydanticBase
from src.domain.commands import ExternalReference
from src.domain.entities import Product
from src.domain.enums import EventTypes


class Message(PydanticBase):
    message_id: UUID = Field(default_factory=uuid4)
    producer: str


class EventMessage(Message):
    event_type: EventTypes
    external_reference: ExternalReference


class OrderMessage(EventMessage):
    order_id: UUID
    aggregate_type: str
    payload: list[Product]


class ProductsPayload(PydanticBase):
    products: list[Product]
    total_price: Decimal


class ProductsReservedMessage(EventMessage):
    event_type: EventTypes = EventTypes.PRODUCTS_RESERVED
    payload: ProductsPayload
