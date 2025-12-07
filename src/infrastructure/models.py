import uuid
from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import UUID, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, NUMERIC
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.domain.aggregates import Order
from src.domain.entities import Product
from src.domain.enums import CreateOrderStepStatus, Currency, OrderStatus


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


class ProductModel(Base, CUModel):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[Decimal] = mapped_column(NUMERIC(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(Enum(Currency), nullable=False)

    order_items: Mapped[List["OrderItemModel"]] = relationship(
        back_populates="product", lazy="selectin"
    )


class OrderItemModel(Base, CUModel):
    __tablename__ = "order_items"

    order_id: Mapped[uuid] = mapped_column(
        ForeignKey("orders.id"), nullable=False, index=True
    )
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(nullable=True)
    price: Mapped[Decimal] = mapped_column(NUMERIC(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(Enum(Currency), nullable=False)

    product: Mapped[ProductModel] = relationship(
        back_populates="order_items",
        lazy="selectin",
    )
    order: Mapped["OrderModel"] = relationship(back_populates="items", lazy="selectin")

    @classmethod
    def from_domain(cls, product: Product, order: Order) -> "OrderItemModel":
        return cls(
            product_id=product.id,
            order_id=order.order_id,
            name=product.name,
            price=Decimal(product.price),
            currency=product.currency,
        )


class OrderModel(Base, CUModel):
    __tablename__ = "orders"

    status: Mapped[str] = mapped_column(Enum(OrderStatus), nullable=False, index=True)

    items: Mapped[List[OrderItemModel]] = relationship(
        back_populates="order", lazy="selectin"
    )

    @classmethod
    def from_domain(cls, order: Order, status: OrderStatus) -> "OrderModel":
        return cls(id=order.order_id, status=status)


class OutboxModel(Base, CUModel):
    __tablename__ = "outbox"

    topic: Mapped[str] = mapped_column(nullable=False)
    message: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_sent: Mapped[bool] = mapped_column(default=False)


class ProcessedMessagesModel(Base, CUModel):
    __tablename__ = "processed_messages"


class CreateOrderSagaStepModel(Base, CUModel):
    __tablename__ = "create_order_saga_step"

    saga_id: Mapped[uuid] = mapped_column(
        ForeignKey("create_order_saga.id"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(Enum(OrderStatus))
    status: Mapped[str] = mapped_column(Enum(CreateOrderStepStatus), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    saga: Mapped["CreateOrderSagaModel"] = relationship(
        back_populates="steps", lazy="selectin"
    )


class CreateOrderSagaModel(Base, CUModel):
    __tablename__ = "create_order_saga"

    order_id: Mapped[uuid] = mapped_column(
        ForeignKey("orders.id"), nullable=False, index=True
    )
    state: Mapped[str] = mapped_column(Enum(OrderStatus), nullable=False)
    current_step_id: Mapped[uuid] = mapped_column(UUID)

    steps: Mapped[List["CreateOrderSagaStepModel"]] = relationship(
        back_populates="saga", lazy="selectin"
    )
