from src.application.disp_depends import DispDepends
from src.application.dispatcher import dispatcher
from src.application.sagas.create_order_saga import CreateOrderSaga
from src.domain.enums import EventTypes
from src.infrastructure.logger.impl import logger
from src.infrastructure.messaging.messages import ProductsReservedMessage
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
