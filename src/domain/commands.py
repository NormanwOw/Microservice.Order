import uuid
from datetime import datetime
from uuid import UUID

from pydantic import Field

from src.domain.base import PydanticBase
from src.domain.entities import Product
from src.domain.enums import AggregateTypes, CommandTypes


class ExternalReference(PydanticBase):
    id: UUID
    type: AggregateTypes
    version: int


class Command(PydanticBase):
    message_id: UUID = Field(default_factory=uuid.uuid4)
    command_type: CommandTypes
    external_reference: ExternalReference | None = None


class CreateOrderCommand(Command):
    command_type: CommandTypes = CommandTypes.CREATE_ORDER
    order_id: UUID = Field(default_factory=uuid.uuid4)
    products: list[Product]
    created_at: datetime = Field(default_factory=datetime.now)
    customer_id: UUID


class SendNotifyCommand(Command):
    command_type: CommandTypes = CommandTypes.SEND_NOTIFY
    customer_id: UUID
    message: str


class ReserveProductsCommand(Command):
    command_type: CommandTypes = CommandTypes.RESERVE_PRODUCTS
    products: list[Product]
