from typing import Any, Optional
from uuid import UUID

from src.domain.base import PydanticBase
from src.domain.enums import CommandTypes, OrderEventTypes, ServiceName


class DomainEvent(PydanticBase):
    pass


class OrderEvent(DomainEvent):
    order_id: UUID | None = None
    payload: dict[Any, Any]


class Event(PydanticBase):
    pass


class StepCompleted(Event):
    saga_id: UUID
    service: ServiceName
    command_type: CommandTypes
    command_payload: Optional[dict[str, Any]] = None
    compensation_command_type: Optional[CommandTypes] = None
    compensation_payload: Optional[dict[str, Any]] = None


class StepCompensated(Event):
    saga_id: UUID
    command_type: CommandTypes
    status: OrderEventTypes


class StepFailed(Event):
    command_type: CommandTypes
