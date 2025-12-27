import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import JSON, UUID, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, NUMERIC
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.domain.aggregates import Order
from src.domain.entities import Product
from src.domain.enums import (
    AggregateTypes,
    CreateOrderSagaStatus,
    CreateOrderStepStatus,
    Currency,
    EventTypes,
    event_type_mapper,
)
from src.domain.events import DomainEvent


class Base(DeclarativeBase):
    id: Mapped[uuid] = mapped_column(
        UUID, nullable=False, primary_key=True, unique=True, default=uuid.uuid4
    )


class CUModel:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, onupdate=datetime.now
    )


class CustomerModel(Base, CUModel):
    __tablename__ = 'customers'

    name: Mapped[str] = mapped_column(nullable=False)


class ProductModel(Base, CUModel):
    __tablename__ = 'products'

    name: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[Decimal] = mapped_column(NUMERIC(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(Enum(Currency), nullable=False)
    stocks: Mapped[int] = mapped_column(nullable=False, default=0)

    order_items: Mapped[List['OrderItemModel']] = relationship(
        back_populates='product', lazy='selectin'
    )

    def to_domain(self) -> Product:
        return Product(
            id=self.id,
            name=self.name,
            price=self.price,
            currency=self.currency,
            quantity=self.stocks,
        )


class OrderItemModel(Base, CUModel):
    __tablename__ = 'order_items'

    order_id: Mapped[uuid] = mapped_column(
        ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True
    )
    product_id: Mapped[str] = mapped_column(
        ForeignKey('products.id', ondelete='SET NULL'), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(nullable=True)
    price: Mapped[Decimal] = mapped_column(NUMERIC(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(Enum(Currency), nullable=False)

    product: Mapped[ProductModel] = relationship(
        back_populates='order_items',
        lazy='selectin',
    )
    order: Mapped['OrderModel'] = relationship(back_populates='items', lazy='selectin')

    @classmethod
    def from_domain(cls, product: Product, order: Order) -> 'OrderItemModel':
        return cls(
            product_id=product.id,
            order_id=order.id,
            name=product.name,
            price=Decimal(product.price),
            currency=product.currency,
            quantity=product.quantity,
        )


class OrderModel(Base, CUModel):
    __tablename__ = 'orders'

    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey('customers.id', ondelete='SET NULL'), nullable=False
    )
    status: Mapped[str] = mapped_column(Enum(EventTypes), nullable=False, index=True)
    version: Mapped[int] = mapped_column(nullable=False)

    items: Mapped[List[OrderItemModel]] = relationship(
        back_populates='order', lazy='selectin'
    )

    @classmethod
    def from_domain(cls, order: Order, status: EventTypes) -> 'OrderModel':
        return cls(id=order.id, status=status, version=order.version)


class OutboxModel(Base, CUModel):
    __tablename__ = 'outbox'

    aggregate_type: Mapped[str] = mapped_column(Enum(AggregateTypes))
    aggregate_id: Mapped[UUID] = mapped_column(nullable=False)
    event_type: Mapped[str] = mapped_column(Enum(EventTypes))
    aggregate_version: Mapped[int] = mapped_column(nullable=False)
    topic: Mapped[str] = mapped_column(nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(
        default=None, nullable=True
    )


class ProcessedMessagesModel(Base, CUModel):
    __tablename__ = 'processed_messages'


class CreateOrderSagaStepModel(Base, CUModel):
    __tablename__ = 'create_order_saga_step'

    saga_id: Mapped[uuid] = mapped_column(
        ForeignKey('create_order_saga.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(Enum(EventTypes))
    status: Mapped[str] = mapped_column(Enum(CreateOrderStepStatus), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    saga: Mapped['CreateOrderSagaModel'] = relationship(
        back_populates='steps', lazy='selectin'
    )


class CreateOrderSagaModel(Base, CUModel):
    __tablename__ = 'create_order_saga'

    order_id: Mapped[uuid] = mapped_column(
        ForeignKey('orders.id'), nullable=False, index=True
    )
    order_version: Mapped[int] = mapped_column(nullable=False)
    state: Mapped[str] = mapped_column(Enum(CreateOrderSagaStatus), nullable=False)
    current_step_id: Mapped[uuid] = mapped_column(UUID)

    steps: Mapped[List['CreateOrderSagaStepModel']] = relationship(
        back_populates='saga', lazy='selectin'
    )


class OrderEventModel(Base, CUModel):
    __tablename__ = 'order_events'

    order_id: Mapped[UUID] = mapped_column(index=True)
    version: Mapped[int] = mapped_column()
    event_type: Mapped[str] = mapped_column(Enum(EventTypes))
    payload: Mapped[dict] = mapped_column(JSON)

    def to_domain(self) -> DomainEvent:
        event = event_type_mapper[self.event_type]
        return event(**self.payload)
