from src.application.disp_depends import DispDepends
from src.application.dispatcher import dispatcher
from src.application.ports.uow import IUnitOfWork
from src.application.sagas.create_order_saga import CreateOrderSaga
from src.application.use_cases.cancel_order import CancelOrder
from src.domain.enums import CommandTypes, OrderEventTypes
from src.infrastructure.logger.impl import logger
from src.infrastructure.messaging.messages import (
    CancelOrderMessage,
    FailedEventMessage,
    PaymentChargedMessage,
    ProductsCommittedMessage,
    ProductsReservedMessage,
)
from src.presentation.dependencies.order_dependencies import OrderDependencies


@dispatcher.register(OrderEventTypes.PRODUCTS_RESERVED)
async def handle_products_reserved(
    uow: IUnitOfWork,
    message: dict,
    saga: CreateOrderSaga = DispDepends(OrderDependencies.create_order_saga),
):
    msg = ProductsReservedMessage(**message)
    await saga.on_products_reserved(uow, msg)
    logger.info(f'Products reserved for order {msg.external_reference.id}')


@dispatcher.register(OrderEventTypes.PAYMENT_CHARGED)
async def handle_payment_charged(
    uow: IUnitOfWork,
    message: dict,
    saga: CreateOrderSaga = DispDepends(OrderDependencies.create_order_saga),
):
    msg = PaymentChargedMessage(**message)
    await saga.on_payment_charged(uow, msg)
    logger.info(f'Payment charged for order {msg.external_reference.id}')


@dispatcher.register(OrderEventTypes.PRODUCTS_COMMITTED)
async def handle_products_committed(
    uow: IUnitOfWork,
    message: dict,
    saga: CreateOrderSaga = DispDepends(OrderDependencies.create_order_saga),
):
    msg = ProductsCommittedMessage(**message)
    await saga.on_products_committed(uow, msg)
    logger.info(f'Products committed for order {msg.external_reference.id}')


@dispatcher.register(OrderEventTypes.CHARGE_PAYMENT_FAILED)
async def handle_charge_payment_failed(
    uow: IUnitOfWork,
    message: dict,
    saga: CreateOrderSaga = DispDepends(OrderDependencies.create_order_saga),
):
    msg = FailedEventMessage(**message)
    await saga.compensate(uow, msg)
    logger.info(
        f'Failed charge payment. {msg.payload.error_message}. Order {msg.external_reference.id}'
    )


@dispatcher.register(OrderEventTypes.RESERVE_FAILED)
async def handle_reserve_products_failed(
    uow: IUnitOfWork,
    message: dict,
    saga: CreateOrderSaga = DispDepends(OrderDependencies.create_order_saga),
):
    msg = FailedEventMessage(**message)
    await saga.compensate(uow, msg)
    logger.info(
        f'Failed reserve products. {msg.payload.error_message}. Order {msg.external_reference.id}'
    )


@dispatcher.register(CommandTypes.CANCEL_ORDER)
async def handle_cancel_order(
    uow: IUnitOfWork,
    message: dict,
    cancel_order: CancelOrder = DispDepends(OrderDependencies.cancel_order),
):
    msg = CancelOrderMessage(**message)
    await cancel_order(uow, msg)
    logger.info(f'Cancelled order {msg.external_reference.id}')
