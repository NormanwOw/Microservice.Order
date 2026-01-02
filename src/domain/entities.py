from decimal import Decimal
from uuid import UUID

from src.domain.base import PydanticBase
from src.domain.enums import Currency


class Product(PydanticBase):
    id: UUID
    name: str
    quantity: int
    price: Decimal
    currency: Currency = Currency.USD
