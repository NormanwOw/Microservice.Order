import uuid

from pydantic import BaseModel

from microservice_order.src.domain.aggregates import Order


class Message(BaseModel):
    message_id: str = str(uuid.uuid4())


class EventMessage(Message):
    event_id: str = str(uuid.uuid4())


class OrderCreatedMessage(EventMessage):
    event_type: str = "OrderCreated"
    aggregate_type: str = "Order"
    payload: Order
