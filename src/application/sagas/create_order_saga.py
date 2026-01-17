from src.domain.commands import SendNotifyCommand
from src.domain.enums import CreateOrderSagaStatus, CreateOrderStepStatus, OrderEventTypes
from src.domain.events import OrderPayed
from src.infrastructure.exceptions import OrderDoesNotExist, SagaDoesNotExist
from src.infrastructure.messaging.messages import ChargedPaymentMessage, OrderMessage
from src.infrastructure.models import (
    CreateOrderSagaModel,
    CreateOrderSagaStepModel,
    OrderModel,
)
from src.infrastructure.services.interfaces import INotificationService, IPaymentService
from src.infrastructure.uow.interfaces import IUnitOfWork


class CreateOrderSaga:
    def __init__(
        self,
        uow: IUnitOfWork,
        payment_service_proxy: IPaymentService,
        notifications_service_proxy: INotificationService,
    ):
        self.uow = uow
        self.payment_service = payment_service_proxy
        self.notifications_service = notifications_service_proxy

    async def on_charged_payment(self, message: ChargedPaymentMessage):
        async with self.uow:
            saga: CreateOrderSagaModel = await self.uow.create_order_saga.find_one(
                CreateOrderSagaModel.order_id, message.order_id
            )

            if not saga:
                raise SagaDoesNotExist

            if saga.state == CreateOrderSagaStatus.COMPLETED:
                return

            customer_id = saga.context['customer_id']
            step = CreateOrderSagaStepModel(
                saga_id=saga.id,
                event_type=OrderEventTypes.ORDER_PAYED,
                status=CreateOrderStepStatus.SUCCESS,
                payload=message.model_dump(),
            )
            await self.uow.create_order_saga_step.add(step)

            order = await self.uow.orders.load(message.order_id)
            event = OrderPayed(order_id=message.order_id)
            await self.uow.orders.append_events(
                order_id=message.order_id,
                expected_version=order.version,
                events=[event],
            )
            order.apply(event)
            await self.uow.orders.upsert_projection(order, customer_id)
            await self.notifications_service.notify(
                SendNotifyCommand(
                    customer_id=saga.context['customer_id'],
                    message=f'Заказ №{message.order_id} успешно оформлен',
                )
            )
            saga.state = CreateOrderSagaStatus.COMPLETED
            await self.uow.commit()

    async def compensate(self, message: OrderMessage):
        async with self.uow:
            saga = await self.uow.create_order_saga.find_one(
                CreateOrderSagaModel.order_id, message.order_id
            )

            if not saga:
                raise SagaDoesNotExist

            step = CreateOrderSagaStepModel(
                saga_id=saga.id,
                event_type=OrderEventTypes.FAILED_CREATE_ORDER,
                status=CreateOrderStepStatus.IN_PROGRESS,
                payload=message.model_dump(),
            )
            await self.uow.create_order_saga_step.add(step)

            order = await self.uow.orders.find_one(
                OrderModel.id,
                message.order_id,
            )
            if not order:
                raise OrderDoesNotExist

            step.status = CreateOrderStepStatus.COMPENSATED
            saga.state = CreateOrderSagaStatus.FAILED

            await self.uow.commit()
