from src.application.disp_depends import DispDepends
from src.application.dispatcher import dispatcher
from src.application.sagas.create_order_saga import CreateOrderSaga
from src.domain.enums import EventTypes
from src.presentation.dependencies.order_dependencies import OrderDependencies


@dispatcher.register(EventTypes.PRODUCTS_RESERVED)
async def handle_products_reserved(
    message: dict,
    saga: CreateOrderSaga = DispDepends(OrderDependencies.create_order_saga),
):
    pass


#
