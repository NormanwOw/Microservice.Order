from uuid import uuid4

from fastapi import APIRouter
from fastapi.params import Depends

from src.application.use_cases.create_order import CreateOrder
from src.config import VERSION
from src.domain.aggregates import Order
from src.presentation.dependencies.order_dependencies import OrderDependencies
from src.presentation.exception_handler import exception_handler
from src.presentation.schemas import CreateOrderSchema

router = APIRouter(prefix=f'/api/v{VERSION}/orders', tags=['Orders'])


@router.post(path='', summary='Создание заказа')
@exception_handler
async def create_order_endpoint(
    order_data: CreateOrderSchema,
    create_order: CreateOrder = Depends(OrderDependencies.create_order),
):
    """Упрощённый вариант без авторизации"""
    order = Order(**order_data.model_dump(), customer_id=uuid4())
    return await create_order(order)
