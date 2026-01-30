from src.domain.commands import ChargePaymentCommand, ChargePaymentPayload
from src.domain.enums import (
    CreateOrderSagaStatus,
    CreateOrderStepStatus,
    OrderEventTypes,
)
from src.domain.events import ProductsReserved
from src.infrastructure.exceptions import OrderDoesNotExist, SagaDoesNotExist
from src.infrastructure.messaging.messages import OrderMessage, ProductsReservedMessage
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
        payment_service_proxy: IPaymentService,
        notifications_service_proxy: INotificationService,
    ):
        self.payment_service = payment_service_proxy
        self.notifications_service = notifications_service_proxy

    async def on_products_reserved(self, uow: IUnitOfWork, message: ProductsReservedMessage):
        order_id = message.external_reference.id
        saga: CreateOrderSagaModel = await uow.create_order_saga.find_one(
            CreateOrderSagaModel.order_id, order_id
        )

        if not saga:
            raise SagaDoesNotExist

        step = CreateOrderSagaStepModel(
            saga_id=saga.id,
            event_type=OrderEventTypes.PRODUCTS_RESERVED,
            status=CreateOrderStepStatus.SUCCESS,
            payload=message.to_dict(),
        )
        await uow.create_order_saga_step.add(step)

        order = await uow.orders.load(order_id=order_id)
        if order is None or order.version != message.external_reference.version:
            raise OrderDoesNotExist

        event = ProductsReserved(payload=message.payload.to_dict(), order_id=order_id)

        await uow.orders.append_events(
            order_id=order_id,
            expected_version=message.external_reference.version,
            events=[event],
        )
        order_version = message.external_reference.version + 1
        message.external_reference.version = order_version
        command = ChargePaymentCommand(
            external_reference=message.external_reference,
            payload=ChargePaymentPayload(
                amount=message.payload.total_price,
                currency=order.products[0].currency,
                user_id=saga.context['customer_id'],
            ),
        )
        await self.payment_service.charge_payment(uow, command)
        step = CreateOrderSagaStepModel(
            saga_id=saga.id,
            event_type=OrderEventTypes.CHARGED_PAYMENT,
            status=CreateOrderStepStatus.IN_PROGRESS,
            payload=command.payload.to_dict(),
        )
        await uow.create_order_saga_step.add(step)
        saga.current_step_id = step.id
        saga.state = CreateOrderSagaStatus.WAITING_PAYMENT
        saga.order_version = order_version
        saga.order.version = order_version

    async def compensate(self, uow: IUnitOfWork, message: OrderMessage):
        saga = await uow.create_order_saga.find_one(CreateOrderSagaModel.order_id, message.order_id)

        if not saga:
            raise SagaDoesNotExist

        step = CreateOrderSagaStepModel(
            saga_id=saga.id,
            event_type=OrderEventTypes.FAILED_CREATE_ORDER,
            status=CreateOrderStepStatus.IN_PROGRESS,
            payload=message.model_dump(),
        )
        await uow.create_order_saga_step.add(step)

        order = await uow.orders.find_one(
            OrderModel.id,
            message.order_id,
        )
        if not order:
            raise OrderDoesNotExist

        step.status = CreateOrderStepStatus.COMPENSATED
        saga.state = CreateOrderSagaStatus.FAILED
