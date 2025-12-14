from fastapi import Request

from src.application.sagas.create_order_saga import CreateOrderSaga
from src.application.use_cases.create_order import CreateOrder
from src.config import settings
from src.infrastructure.services.payment_service_proxy import PaymentServiceProxy
from src.infrastructure.uow.impl import get_uow


class OrderDependencies:
    @classmethod
    async def create_order(cls, request: Request):
        producer = request.scope['app'].state.producer
        return CreateOrder(get_uow(), producer, settings)

    @classmethod
    async def create_order_saga(cls) -> CreateOrderSaga:
        uow = get_uow()
        return CreateOrderSaga(uow, PaymentServiceProxy(uow, settings))
