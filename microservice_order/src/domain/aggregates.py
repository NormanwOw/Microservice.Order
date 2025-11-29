import uuid

from pydantic import BaseModel

from microservice_order.src.domain.entities import Product


class Order(BaseModel):
    order_id: str = str(uuid.uuid4())
    customer_id: str
    items: list[Product]
