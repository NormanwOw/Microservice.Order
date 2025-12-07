from uuid import UUID

from pydantic import BaseModel

from src.domain.entities import Product


class CreateOrderSchema(BaseModel):
    products: list[Product]


class CreateOrderResponse(BaseModel):
    order_id: UUID
