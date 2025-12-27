import uuid
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.entities import Product


class Command(BaseModel):
    pass


class CreateOrderCommand(Command):
    order_id: UUID = Field(default_factory=uuid.uuid4)
    products: list[Product]
    created_at: datetime = Field(default_factory=datetime.now)
    customer_id: UUID
