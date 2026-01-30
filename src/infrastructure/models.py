import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import UUID, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.domain.aggregates import Order
from src.domain.enums import (
    CreateOrderSagaStatus,
    CreateOrderStepStatus,
    OrderEventTypes,
)
from src.domain.events import DomainEvent
from src.domain.mappers import event_type_mapper


class Base(DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID, nullable=False, primary_key=True, default=uuid.uuid4
    )


class CUModel:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(timezone.utc)
    )


class OrderModel(Base, CUModel):
    __tablename__ = 'orders'

    customer_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    status: Mapped[str] = mapped_column(Enum(OrderEventTypes), nullable=False, index=True)
    version: Mapped[int] = mapped_column(nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    saga: Mapped['CreateOrderSagaModel'] = relationship(back_populates='order', lazy='selectin')

    @classmethod
    def from_domain(cls, order: Order, status: OrderEventTypes) -> 'OrderModel':
        return cls(id=order.id, status=status, version=order.version)


class OutboxModel(Base, CUModel):
    __tablename__ = 'outbox'

    action: Mapped[str] = mapped_column(nullable=False)
    topic: Mapped[str] = mapped_column(nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    external_reference: Mapped[dict] = mapped_column(JSONB, nullable=False)
    producer: Mapped[str] = mapped_column(nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )


class ProcessedMessagesModel(Base, CUModel):
    __tablename__ = 'processed_messages'


class CreateOrderSagaStepModel(Base, CUModel):
    __tablename__ = 'create_order_saga_step'

    saga_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('create_order_saga.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    event_type: Mapped[OrderEventTypes] = mapped_column(Enum(OrderEventTypes))
    status: Mapped[str] = mapped_column(Enum(CreateOrderStepStatus), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    saga: Mapped['CreateOrderSagaModel'] = relationship(back_populates='steps', lazy='selectin')


class CreateOrderSagaModel(Base, CUModel):
    __tablename__ = 'create_order_saga'

    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('orders.id'), nullable=False, index=True)
    order_version: Mapped[int] = mapped_column(nullable=False)
    state: Mapped[str] = mapped_column(Enum(CreateOrderSagaStatus), nullable=False)
    current_step_id: Mapped[uuid.UUID] = mapped_column(UUID)
    context: Mapped[dict] = mapped_column(JSONB, nullable=False)
    steps: Mapped[List['CreateOrderSagaStepModel']] = relationship(
        back_populates='saga', lazy='selectin'
    )

    order: Mapped[OrderModel] = relationship(back_populates='saga', lazy='selectin')


class OrderEventModel(Base, CUModel):
    __tablename__ = 'order_events'

    order_id: Mapped[uuid.UUID] = mapped_column(UUID, index=True)
    version: Mapped[int] = mapped_column()
    event_type: Mapped[str] = mapped_column(Enum(OrderEventTypes))
    payload: Mapped[dict] = mapped_column(JSONB)

    def to_domain(self) -> DomainEvent:
        event = event_type_mapper[self.event_type]
        return event(**self.payload)
