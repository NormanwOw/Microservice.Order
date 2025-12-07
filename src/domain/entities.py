from pydantic import BaseModel

from src.domain.enums import Currency


class Product(BaseModel):
    id: str
    name: str
    quantity: int
    price: str
    currency: Currency = Currency.USD
