from src.application.disp_depends import DispDepends
from src.application.dispatcher import dispatcher
from src.application.sagas.create_order_saga import CreateOrderSaga
from src.domain.enums import OrderStatus
from src.infrastructure.logger.impl import logger
from src.infrastructure.messaging.messages import OrderMessage
from src.presentation.dependencies.order_dependencies import OrderDependencies


@dispatcher.register(OrderStatus.ORDER_CREATED)
async def handle_create_order(
    message: dict,
    saga: CreateOrderSaga = DispDepends(OrderDependencies.create_order_saga),
):
    message = OrderMessage(**message)
    logger.info('[ORDER] Creating order')
    await saga.on_order_created(message)


@dispatcher.register(OrderStatus.FAILED)
async def handle_cancel_order(
    message: dict,
    saga: CreateOrderSaga = DispDepends(OrderDependencies.create_order_saga),
):
    message = OrderMessage(**message)
    logger.info('[ORDER] Cancel order')
    await saga.compensate(message)
