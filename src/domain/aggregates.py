import json
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.commands import CreateOrderCommand
from src.domain.entities import Product
from src.domain.enums import AggregateType, OrderEventTypes
from src.domain.events import (
    DomainEvent,
    FailedCreateOrder,
    OrderCreated,
    OrderPayed,
    ProductsReserved,
)
from src.domain.exceptions import EventNotSupported, OrderAlreadyExists
from src.domain.mappers import event_type_mapper


class Aggregate(BaseModel):
    id: UUID | None = None
    status: OrderEventTypes | None = None
    version: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)
    type: AggregateType

    def to_dict(self) -> dict:
        return json.loads(self.model_dump_json())


class Order(Aggregate):
    products: list[Product] | None = None
    type: AggregateType = AggregateType.ORDER

    def decide(self, command: CreateOrderCommand) -> list[DomainEvent]:
        if self.id is not None:
            raise OrderAlreadyExists

        return [OrderCreated(**command.model_dump())]

    def apply(self, event):
        if event.__class__.__name__ not in [
            mapped_event.__name__ for mapped_event in event_type_mapper.values()
        ]:
            raise EventNotSupported

        if isinstance(event, OrderCreated):
            self.id = event.order_id
            self.status = OrderEventTypes.ORDER_CREATED
            self.products = event.products

        elif isinstance(event, ProductsReserved):
            self.status = OrderEventTypes.PRODUCTS_RESERVED

        elif isinstance(event, OrderPayed):
            self.status = OrderEventTypes.ORDER_PAYED

        elif isinstance(event, FailedCreateOrder):
            self.status = OrderEventTypes.FAILED_CREATE_ORDER

        self.version += 1
