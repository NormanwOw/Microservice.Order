from fastapi import Request

from src.application.use_cases.create_order import CreateOrder
from src.config import settings
from src.infrastructure.uow.impl import get_uow


class OrderDependencies:
    @classmethod
    async def create_order(cls, request: Request):
        producer = request.scope['app'].state.producer
        return CreateOrder(get_uow(), producer, settings)
