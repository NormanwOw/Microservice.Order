import json
from uuid import uuid4

from src.config import Settings
from src.domain.aggregates import Order
from src.domain.enums import CreateOrderStepStatus, OrderStatus
from src.infrastructure.messaging.interfaces import IKafkaProducer
from src.infrastructure.messaging.messages import OrderMessage
from src.infrastructure.models import (
    CreateOrderSagaModel,
    CreateOrderSagaStepModel,
    OrderModel,
    OutboxModel,
)
from src.infrastructure.uow.interfaces import IUnitOfWork
from src.presentation.schemas import CreateOrderResponse


class CreateOrder:
    def __init__(self, uow: IUnitOfWork, producer: IKafkaProducer, settings: Settings):
        self.uow = uow
        self.producer = producer
        self.settings = settings

    async def __call__(self, order: Order) -> CreateOrderResponse:
        async with self.uow:
            await self.save_order(order)
            message = await self.create_message(order)
            await self.save_message_to_outbox(message)
            await self.save_data_to_saga(order, message)
            await self.uow.commit()

            return CreateOrderResponse(order_id=order.order_id)

    async def save_order(self, order: Order):
        new_order = OrderModel.from_domain(order, status=OrderStatus.ORDER_CREATED)
        await self.uow.orders.add(new_order)

    async def create_message(self, order: Order) -> dict:
        return json.loads(
            OrderMessage(
                order_id=order.order_id,
                event_type=OrderStatus.ORDER_CREATED,
                aggregate_type="Order",
                payload=order.products,
            ).model_dump_json()
        )

    async def save_message_to_outbox(self, message: dict):
        for_outbox = OutboxModel(
            topic=self.settings.ORDER_EVENTS_TOPIC, message=message
        )
        await self.uow.outbox.add(for_outbox)

    async def save_data_to_saga(self, order: Order, message: dict):
        step_id = uuid4()
        saga_step = CreateOrderSagaStepModel(
            id=step_id,
            event_type=OrderStatus.ORDER_CREATED,
            status=CreateOrderStepStatus.SUCCESS,
            payload=message,
        )
        saga = CreateOrderSagaModel(
            order_id=order.order_id,
            state=OrderStatus.ORDER_CREATED,
            current_step_id=step_id,
        )
        saga.steps.append(saga_step)
        await self.uow.create_order_saga.add(saga)
