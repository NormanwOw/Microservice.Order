from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.aggregates import Order
from src.domain.events import DomainEvent
from src.domain.exceptions import ConcurrencyException
from src.infrastructure.models import OrderEventModel, OrderModel
from src.infrastructure.repositories.base_repository import SQLAlchemyRepository
from src.infrastructure.repositories.interfaces import IOrderRepository


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

        order = Order()
        for event_model in events:
            event = event_model.to_domain()
            order.apply(event)

        return order

    async def append_events(self, order_id: UUID, expected_version: int, events: list[DomainEvent]):
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
            self.__session.add(
                OrderEventModel(
                    order_id=order_id,
                    version=expected_version + i,
                    event_type=event.__class__.__name__,
                    payload=event.to_dict(),
                )
            )

    async def upsert_projection(self, order: Order, customer_id: UUID):
        stmt = insert(OrderModel).values(
            id=order.id,
            status=order.status,
            version=order.version,
            customer_id=customer_id,
            payload=[product.to_dict() for product in order.products],
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=[OrderModel.id],
            set_={
                'status': stmt.excluded.status,
                'version': stmt.excluded.version,
            },
        )
        await self.__session.execute(stmt)
