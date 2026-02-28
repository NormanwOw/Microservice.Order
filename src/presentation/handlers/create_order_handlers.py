from src.application.disp_depends import DispDepends
from src.application.dispatcher import dispatcher
from src.application.sagas.create_order_saga import CreateOrderSaga
from src.domain.enums import EventTypes
from src.infrastructure.logger.impl import logger
from src.infrastructure.messaging.messages import (
    PaymentChargedMessage,
    ProductsCommittedMessage,
    ProductsReservedMessage,
)
from src.infrastructure.uow.interfaces import IUnitOfWork
from src.presentation.dependencies.order_dependencies import OrderDependencies


@dispatcher.register(EventTypes.PRODUCTS_RESERVED)
async def handle_products_reserved(
    uow: IUnitOfWork,
    message: dict,
    saga: CreateOrderSaga = DispDepends(OrderDependencies.create_order_saga),
):
    msg = ProductsReservedMessage(**message)
    await saga.on_products_reserved(uow, msg)
    logger.info(f'Products reserved for order {msg.external_reference.id}')


@dispatcher.register(EventTypes.PAYMENT_CHARGED)
async def handle_payment_charged(
    uow: IUnitOfWork,
    message: dict,
    saga: CreateOrderSaga = DispDepends(OrderDependencies.create_order_saga),
):
    msg = PaymentChargedMessage(**message)
    await saga.on_payment_charged(uow, msg)
    logger.info(f'Payment charged for order {msg.external_reference.id}')


@dispatcher.register(EventTypes.PRODUCTS_COMMITTED)
async def handle_products_committed(
    uow: IUnitOfWork,
    message: dict,
    saga: CreateOrderSaga = DispDepends(OrderDependencies.create_order_saga),
):
    msg = ProductsCommittedMessage(**message)
    await saga.on_products_committed(uow, msg)
    logger.info(f'Products committed for order {msg.external_reference.id}')
