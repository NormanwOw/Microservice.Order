from uuid import UUID

from src.application.ports.services import (
    INotificationService,
    IPaymentService,
    IStocksServiceProxy,
)
from src.application.ports.uow import IUnitOfWork
from src.domain.aggregates import Order
from src.domain.commands import (
    ChargePaymentCommand,
    ChargePaymentPayload,
    CommitProductsCommand,
    SendSuccessCreatedOrderNotifyCommand,
    SuccessCreatedOrderNotifyPayload,
)
from src.domain.entities import Product
from src.domain.enums import (
    CreateOrderSagaStatus,
    CreateOrderStepStatus,
    OrderEventTypes,
)
from src.domain.events import PaymentCharged, ProductsCommitted, ProductsReserved
from src.infrastructure.exceptions import OrderDoesNotExist, SagaDoesNotExist
from src.infrastructure.messaging.messages import (
    OrderMessage,
    PaymentChargedMessage,
    ProductsCommittedMessage,
    ProductsReservedMessage,
)
from src.infrastructure.models import (
    CreateOrderSagaModel,
    CreateOrderSagaStepModel,
    OrderModel,
)


class CreateOrderSaga:
    def __init__(
        self,
        stocks_service_proxy: IStocksServiceProxy,
        payment_service_proxy: IPaymentService,
        notifications_service_proxy: INotificationService,
    ):
        self.stocks_service = stocks_service_proxy
        self.payment_service = payment_service_proxy
        self.notifications_service = notifications_service_proxy

    async def get_saga(self, uow: IUnitOfWork, order_id: UUID) -> CreateOrderSagaModel:
        saga: CreateOrderSagaModel = await uow.create_order_saga.find_one(
            CreateOrderSagaModel.order_id, order_id
        )
        if not saga:
            raise SagaDoesNotExist

        return saga

    async def get_order(self, uow: IUnitOfWork, order_id: UUID, aggregate_version: int) -> Order:
        order: Order = await uow.orders.load(order_id=order_id)
        if order is None or order.version != aggregate_version:
            raise OrderDoesNotExist

        return order

    async def on_products_reserved(self, uow: IUnitOfWork, message: ProductsReservedMessage):
        order_id = message.external_reference.id
        saga = await self.get_saga(uow, order_id)

        step = CreateOrderSagaStepModel(
            saga_id=saga.id,
            event_type=OrderEventTypes.PRODUCTS_RESERVED,
            status=CreateOrderStepStatus.SUCCESS,
            payload=message.to_dict(),
        )
        await uow.create_order_saga_step.add(step)

        order = await self.get_order(uow, order_id, message.external_reference.version)
        event = ProductsReserved(payload=message.payload.to_dict(), order_id=order_id)

        await uow.orders.append_events(
            order_id=order_id,
            expected_version=message.external_reference.version,
            events=[event],
        )
        message.external_reference.version += 1
        order_version = message.external_reference.version
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

    async def on_payment_charged(self, uow: IUnitOfWork, message: PaymentChargedMessage):
        order_id = message.external_reference.id
        saga = await self.get_saga(uow, order_id)
        event = PaymentCharged(order_id=order_id)

        products = []
        for step in saga.steps:
            if step.event_type == OrderEventTypes.PRODUCTS_RESERVED:
                for product in step.payload['payload']['products']:
                    products.append(Product(**product))
                continue
            if step.event_type == OrderEventTypes.PAYMENT_CHARGED:
                step.status = CreateOrderStepStatus.SUCCESS
                event.payload = step.payload
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

    async def on_products_committed(self, uow: IUnitOfWork, message: ProductsCommittedMessage):
        order_id = message.external_reference.id
        saga = await self.get_saga(uow, order_id)

        event = ProductsCommitted(payload=message.payload)

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

        command = SendSuccessCreatedOrderNotifyCommand(
            external_reference=message.external_reference,
            payload=SuccessCreatedOrderNotifyPayload(
                user_id=saga.context['customer_id'], products=message.payload.products
            ),
        )
        await self.notifications_service.notify_success_created_order(uow, command)
        step = CreateOrderSagaStepModel(
            saga_id=saga.id,
            event_type=OrderEventTypes.NOTIFIED_CUSTOMER_SUCCESS_ORDER_CREATED,
            status=CreateOrderStepStatus.IN_PROGRESS,
            payload=command.payload.to_dict(),
        )

        await uow.create_order_saga_step.add(step)
        saga.current_step_id = step.id
        saga.state = CreateOrderSagaStatus.WAITING_NOTIFY_ORDER_COMPLETED
        saga.order.status = OrderEventTypes.PRODUCTS_COMMITTED
        saga.order_version = order_version
        saga.order.version = order_version

    async def compensate(self, uow: IUnitOfWork, message: OrderMessage):
        saga = await self.get_saga(uow, message.order_id)
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
