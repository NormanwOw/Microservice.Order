from typing import cast
from uuid import UUID

from src.application.ports.services import (
    BaseService,
    INotificationService,
    IOrderServiceProxy,
    IPaymentService,
    IStocksServiceProxy,
)
from src.application.ports.uow import IUnitOfWork
from src.domain.aggregates import Order
from src.domain.commands import (
    CancelCommand,
    ChargePaymentCommand,
    CommitProductsCommand,
    NotifyCommand,
    PaymentPayload,
)
from src.domain.entities import Product
from src.domain.enums import (
    CommandTypes,
    CreateOrderSagaStatus,
    CreateOrderStepStatus,
    EventTypes,
    OrderEventTypes,
    ServiceName,
)
from src.domain.events import StepCompensated, StepCompleted
from src.infrastructure.exceptions import OrderDoesNotExist, SagaDoesNotExist
from src.infrastructure.messaging.messages import (
    FailedEventMessage,
    PaymentChargedMessage,
    ProductsCommittedMessage,
    ProductsReservedMessage,
)
from src.infrastructure.models import (
    CreateOrderSagaModel,
    CreateOrderSagaStepModel,
    OrderEventModel,
)


class CreateOrderSaga:
    def __init__(
        self,
        order_service_proxy: IOrderServiceProxy,
        stocks_service_proxy: IStocksServiceProxy,
        payment_service_proxy: IPaymentService,
        notifications_service_proxy: INotificationService,
    ):
        self.stocks_service = stocks_service_proxy
        self.payment_service = payment_service_proxy
        self.notifications_service = notifications_service_proxy
        self.service_mapper = {
            ServiceName.ORDER: order_service_proxy,
            ServiceName.PAYMENT: payment_service_proxy,
            ServiceName.STOCKS: stocks_service_proxy,
            ServiceName.NOTIFICATION: notifications_service_proxy,
        }

    async def get_saga(self, uow: IUnitOfWork, order_id: UUID) -> CreateOrderSagaModel:
        saga = cast(
            CreateOrderSagaModel,
            await uow.create_order_saga.find_one(CreateOrderSagaModel.order_id, order_id),
        )
        if not saga:
            raise SagaDoesNotExist

        return saga

    async def get_order(self, uow: IUnitOfWork, order_id: UUID, aggregate_version: int) -> Order:
        order: Order | None = await uow.orders.load(order_id=order_id)
        if order is None or order.version != aggregate_version:
            raise OrderDoesNotExist

        return order

    async def on_products_reserved(
        self, uow: IUnitOfWork, message: ProductsReservedMessage
    ) -> None:
        order_id = message.external_reference.id
        saga = await self.get_saga(uow, order_id)

        order = await self.get_order(uow, order_id, message.external_reference.version)

        message.external_reference.version += 1
        order_version = message.external_reference.version

        step = CreateOrderSagaStepModel(
            saga_id=saga.id,
            event_type=OrderEventTypes.PRODUCTS_RESERVED,
            status=CreateOrderStepStatus.SUCCESS,
            payload=message.to_dict(),
        )
        await uow.create_order_saga_step.add(step)
        command = ChargePaymentCommand(
            external_reference=message.external_reference,
            payload=PaymentPayload(
                amount=message.payload.total_price,
                currency=order.products[0].currency,
                user_id=saga.context['customer_id'],
            ),
        )

        event = StepCompleted(
            saga_id=saga.id,
            service=ServiceName.STOCKS,
            command_type=CommandTypes.RESERVE_PRODUCTS,
            command_payload=message.payload.to_dict(),
            compensation_command_type=CommandTypes.CANCEL_RESERVE,
            compensation_payload={'products': [product.to_dict() for product in order.products]},
        )

        await uow.orders.append_events(
            order_id=order_id,
            expected_version=message.external_reference.version - 1,
            events=[event],
        )

        await self.payment_service.charge_payment(uow, command)
        step = CreateOrderSagaStepModel(
            saga_id=saga.id,
            event_type=OrderEventTypes.PAYMENT_CHARGED,
            status=CreateOrderStepStatus.IN_PROGRESS,
            payload=command.payload.to_dict(),
        )
        await uow.create_order_saga_step.add(step)
        saga.current_step_id = step.id
        saga.state = CreateOrderSagaStatus.WAITING_PAYMENT
        saga.order.status = OrderEventTypes.PRODUCTS_RESERVED
        saga.order_version = order_version
        saga.order.version = order_version

    async def on_payment_charged(self, uow: IUnitOfWork, message: PaymentChargedMessage) -> None:
        order_id = message.external_reference.id
        saga = await self.get_saga(uow, order_id)
        event = StepCompleted(
            saga_id=saga.id,
            service=ServiceName.STOCKS,
            command_type=CommandTypes.CHARGE_PAYMENT,
            compensation_command_type=CommandTypes.CANCEL_PAYMENT,
        )
        products = []
        for step in saga.steps:
            if step.event_type == OrderEventTypes.PRODUCTS_RESERVED:
                products = [Product(**product) for product in step.payload['payload']['products']]
                continue
            if step.event_type == OrderEventTypes.PAYMENT_CHARGED:
                step.status = CreateOrderStepStatus.SUCCESS
                event.command_payload = step.payload
                event.compensation_payload = step.payload
                break

        await uow.orders.append_events(
            order_id=order_id,
            expected_version=message.external_reference.version,
            events=[event],
        )
        message.external_reference.version += 1
        order_version = message.external_reference.version

        command = CommitProductsCommand(
            external_reference=message.external_reference, products=products
        )
        await self.stocks_service.commit_products(uow, command)
        step = CreateOrderSagaStepModel(
            saga_id=saga.id,
            event_type=OrderEventTypes.PRODUCTS_COMMITTED,
            status=CreateOrderStepStatus.IN_PROGRESS,
            payload={'products': [product.to_dict() for product in products]},
        )

        await uow.create_order_saga_step.add(step)
        saga.current_step_id = step.id
        saga.state = CreateOrderSagaStatus.WAITING_PRODUCTS_COMMITTED
        saga.order.status = OrderEventTypes.PAYMENT_CHARGED
        saga.order_version = order_version
        saga.order.version = order_version

    async def on_products_committed(
        self, uow: IUnitOfWork, message: ProductsCommittedMessage
    ) -> None:
        order_id = message.external_reference.id
        saga = await self.get_saga(uow, order_id)

        event = StepCompleted(
            saga_id=saga.id,
            service=ServiceName.STOCKS,
            command_type=CommandTypes.COMMIT_PRODUCTS,
            command_payload={
                'products': [product.to_dict() for product in message.payload.products]
            },
        )
        for step in saga.steps:
            if step.event_type == OrderEventTypes.PRODUCTS_COMMITTED:
                step.status = CreateOrderStepStatus.SUCCESS
                break

        await uow.orders.append_events(
            order_id=order_id,
            expected_version=message.external_reference.version,
            events=[event],
        )
        message.external_reference.version += 1
        order_version = message.external_reference.version

        command = NotifyCommand(
            command_type=CommandTypes.SEND_SUCCESS_NOTIFY,
            external_reference=message.external_reference,
            payload={
                'user_id': saga.context['customer_id'],
                'products': [product.to_dict() for product in message.payload.products],
            },
        )
        await self.notifications_service.notify(uow, command)
        step = CreateOrderSagaStepModel(
            saga_id=saga.id,
            event_type=OrderEventTypes.NOTIFIED_CUSTOMER_SUCCESS_ORDER_CREATED,
            status=CreateOrderStepStatus.IN_PROGRESS,
            payload=command.payload,
        )

        await uow.create_order_saga_step.add(step)
        saga.current_step_id = step.id
        saga.state = CreateOrderSagaStatus.WAITING_NOTIFY_ORDER_COMPLETED
        saga.order.status = OrderEventTypes.PRODUCTS_COMMITTED
        saga.order_version = order_version
        saga.order.version = order_version

    async def compensate(self, uow: IUnitOfWork, message: FailedEventMessage) -> None:
        order_id = message.external_reference.id
        saga = await self.get_saga(uow, order_id)
        events: list[OrderEventModel] = await uow.order_events.load_stream(order_id)
        completed_steps = [e for e in events if e.event_type == EventTypes.STEP_COMPLETED]

        for saga_step in saga.steps:
            if saga_step.event_type == message.payload.failed_event:
                saga_step.status = CreateOrderStepStatus.FAILED
                break

        compensation_events = []
        for step in reversed(completed_steps):
            if not step.payload.get('compensation_command_type'):
                continue

            if step.payload['service'] == ServiceName.ORDER:
                step.payload['compensation_payload'] = {'status': message.action}

            service: BaseService = self.service_mapper[step.payload['service']]
            cancel_command = CancelCommand(
                command_type=step.payload['compensation_command_type'],
                external_reference=message.external_reference,
                payload=step.payload['compensation_payload'],
            )
            await service.compensate(uow, cancel_command)
            compensation_events.append(
                StepCompensated(
                    saga_id=saga.id,
                    command_type=step.payload['command_type'],
                    status=message.action,
                )
            )

        if compensation_events:
            await uow.orders.append_events(
                order_id=order_id,
                expected_version=message.external_reference.version,
                events=compensation_events,
            )
        order_version = message.external_reference.version + 1
        saga.state = CreateOrderSagaStatus.COMPENSATED
        saga.order_version = order_version
        saga.order.version = order_version
        command = NotifyCommand(
            command_type=CommandTypes.SEND_FAILED_NOTIFY,
            external_reference=message.external_reference,
            payload={
                'user_id': saga.context['customer_id'],
                'error_message': message.payload.error_message,
            },
        )
        await self.notifications_service.notify(uow, command)
