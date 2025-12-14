from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.domain.enums import Currency


class Product(BaseModel):
    id: UUID
    name: str
    quantity: int
    price: Decimal
    currency: Currency = Currency.USD
