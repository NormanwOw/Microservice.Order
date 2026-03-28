from datetime import datetime
from uuid import UUID

from pydantic import Field

from src.domain.base import PydanticBase
from src.domain.entities import Product
from src.domain.enums import AggregateType, CommandTypes, OrderEventTypes
from src.domain.events import StepCompensated, StepCompleted, StepFailed


class Aggregate(PydanticBase):
    id: UUID | None = None
    status: OrderEventTypes | None = None
    version: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)
    type: AggregateType


class Order(Aggregate):
    products: list[Product]
    type: AggregateType = AggregateType.ORDER

    def apply(self, event: StepCompleted | StepCompensated | StepFailed) -> None:
        if isinstance(event, StepCompleted):
            if event.command_type == CommandTypes.CREATE_ORDER and event.command_payload:
                self.id = event.command_payload['external_reference']['id']
                self.status = OrderEventTypes.ORDER_CREATED

                products = event.command_payload.get('products')
                if products and products:
                    self.products.extend([Product(**p) for p in products])

        elif event.command_type == CommandTypes.RESERVE_PRODUCTS:
            self.status = OrderEventTypes.PRODUCTS_RESERVED

        elif event.command_type == CommandTypes.CHARGE_PAYMENT:
            self.status = OrderEventTypes.PAYMENT_CHARGED

        elif event.command_type == CommandTypes.COMMIT_PRODUCTS:
            self.status = OrderEventTypes.PRODUCTS_COMMITTED

        if isinstance(event, StepFailed):
            self.status = OrderEventTypes.FAILED_CREATE_ORDER

        if isinstance(event, StepCompensated):
            self.status = event.status

        self.version += 1
