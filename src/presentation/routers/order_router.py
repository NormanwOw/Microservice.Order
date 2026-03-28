import uuid
from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from src.application.use_cases.create_order import CreateOrder
from src.config import VERSION
from src.domain.commands import CreateOrderCommand
from src.presentation.dependencies.order_dependencies import OrderDependencies
from src.presentation.schemas import CreateOrderResponse, CreateOrderSchema

router = APIRouter(prefix=f'/api/v{VERSION}/orders', tags=['Orders'])


@router.post(path='', summary='Создание заказа', status_code=201)
async def create_order_endpoint(
    customer_id: uuid.UUID,
    order_data: CreateOrderSchema,
    create_order: Annotated[CreateOrder, Depends(OrderDependencies.create_order)],
) -> CreateOrderResponse:
    """Упрощённый вариант без авторизации"""
    command = CreateOrderCommand(**order_data.model_dump(), customer_id=customer_id)
    return await create_order(command)
