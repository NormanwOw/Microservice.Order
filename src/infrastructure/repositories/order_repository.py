from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repositories import IOrderRepository
from src.domain.aggregates import Order
from src.domain.events import Event
from src.domain.exceptions import ConcurrencyException
from src.domain.mappers import event_type_mapper
from src.infrastructure.models import OrderEventModel, OrderModel
from src.infrastructure.repositories.base_repository import SQLAlchemyRepository


class OrderRepository(SQLAlchemyRepository, IOrderRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, OrderModel)

    async def load(self, order_id: UUID) -> Order | None:
        res = await self.__session.scalars(
            select(OrderEventModel).filter_by(order_id=order_id).order_by(OrderEventModel.version)
        )
        events = res.all()

        if not events:
            return None

        order = Order(products=[])
        for event_model in events:
            domain_event = event_model.to_domain()
            if not domain_event:
                continue
            order.apply(domain_event)

        return order

    async def append_events(
        self, order_id: UUID, expected_version: int, events: Sequence[Event]
    ) -> None:
        res = await self.__session.scalars(
            select(OrderEventModel.version)
            .filter_by(order_id=order_id)
            .order_by(OrderEventModel.version.desc())
            .limit(1)
        )
        current_version = res.first()

        current_version = current_version or 0

        if current_version != expected_version:
            raise ConcurrencyException(f'Expected {expected_version}, got {current_version}')

        for i, event in enumerate(events, start=1):
            new_event = OrderEventModel(
                order_id=order_id,
                version=expected_version + i,
                event_type=event_type_mapper[event.__class__.__name__],
                payload=event.to_dict(),
            )
            self.__session.add(new_event)

    async def upsert_projection(self, order: Order, customer_id: UUID) -> None:
        stmt = insert(OrderModel).values(
            id=order.id,
            status=order.status,
            version=order.version,
            customer_id=customer_id,
            payload={'products': [product.to_dict() for product in order.products]},
        )
        await self.__session.execute(stmt)
