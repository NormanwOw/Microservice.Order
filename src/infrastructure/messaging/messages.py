from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.domain.entities import Product


class Message(BaseModel):
    message_id: UUID = Field(default_factory=uuid4)


class EventMessage(Message):
    event_id: UUID = Field(default_factory=uuid4)


class OrderMessage(EventMessage):
    order_id: UUID
    event_type: str
    aggregate_type: str
    payload: list[Product]
