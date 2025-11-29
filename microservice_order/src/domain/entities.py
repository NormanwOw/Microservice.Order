import uuid
from typing import Literal

from pydantic import BaseModel


class Product(BaseModel):
    product_id: str = str(uuid.uuid4())
    quantity: int
    price: str
    currency: Literal["$", "€"] = "$"
