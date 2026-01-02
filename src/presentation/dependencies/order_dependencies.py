from src.application.sagas.create_order_saga import CreateOrderSaga
from src.application.use_cases.create_order import CreateOrder
from src.config import settings
from src.infrastructure.services.notification_service_proxy import NotificationServiceProxy
from src.infrastructure.services.payment_service_proxy import PaymentServiceProxy
from src.infrastructure.services.stocks_service_proxy import StocksServiceProxy
from src.infrastructure.uow.impl import get_uow


class OrderDependencies:
    @classmethod
    async def create_order(cls):
        uow = get_uow()
        return CreateOrder(uow, StocksServiceProxy(uow, settings), settings)

    @classmethod
    async def create_order_saga(cls) -> CreateOrderSaga:
        uow = get_uow()
        return CreateOrderSaga(
            uow, PaymentServiceProxy(uow, settings), NotificationServiceProxy(uow, settings)
        )
