import json
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.entities import Product
from src.domain.enums import AggregateType, CommandTypes, OrderEventTypes
from src.domain.events import StepCompensated, StepCompleted, StepFailed


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

    def apply(self, event: StepCompleted | StepCompensated | StepFailed):
        if event.command_type == CommandTypes.CREATE_ORDER:
            self.id = event.command_payload['external_reference']['id']
            self.status = OrderEventTypes.ORDER_CREATED
            self.products = [Product(**product) for product in event.command_payload['products']]

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
