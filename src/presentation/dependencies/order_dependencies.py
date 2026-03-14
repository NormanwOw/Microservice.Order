from src.application.sagas.create_order_saga import CreateOrderSaga
from src.application.use_cases.cancel_order import CancelOrder
from src.application.use_cases.create_order import CreateOrder
from src.config import settings
from src.infrastructure.logger.impl import logger
from src.infrastructure.services.notification_service_proxy import NotificationServiceProxy
from src.infrastructure.services.order_service_proxy import OrderServiceProxy
from src.infrastructure.services.payment_service_proxy import PaymentServiceProxy
from src.infrastructure.services.stocks_service_proxy import StocksServiceProxy
from src.infrastructure.uow.impl import get_uow


class OrderDependencies:
    order_service = OrderServiceProxy(settings)
    stocks_service = StocksServiceProxy(settings)
    payment_service = PaymentServiceProxy(settings)
    notification_service = NotificationServiceProxy(settings)

    @classmethod
    async def create_order(cls):
        return CreateOrder(get_uow(), cls.stocks_service, settings, logger)

    @classmethod
    async def create_order_saga(cls) -> CreateOrderSaga:
        return CreateOrderSaga(
            cls.order_service, cls.stocks_service, cls.payment_service, cls.notification_service
        )

    @classmethod
    async def cancel_order(cls):
        return CancelOrder()
