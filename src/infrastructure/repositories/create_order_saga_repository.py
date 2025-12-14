import json
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.enums import CreateOrderStepStatus, OrderStatus
from src.infrastructure.messaging.messages import OrderMessage
from src.infrastructure.models import CreateOrderSagaModel, CreateOrderSagaStepModel
from src.infrastructure.repositories.base_repository import SQLAlchemyRepository
from src.infrastructure.repositories.interfaces import ICreateOrderSagaRepository


class CreateOrderSagaRepository(SQLAlchemyRepository, ICreateOrderSagaRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, CreateOrderSagaModel)

    async def create(self, message: OrderMessage):
        saga_id = uuid4()
        step_id = uuid4()
        saga_step = CreateOrderSagaStepModel(
            id=step_id,
            saga_id=saga_id,
            event_type=OrderStatus.PAYMENT_PENDING,
            status=CreateOrderStepStatus.IN_PROGRESS,
            payload=json.loads(message.model_dump_json()),
        )
        saga = CreateOrderSagaModel(
            id=saga_id,
            order_id=message.order_id,
            state=OrderStatus.PAYMENT_PENDING,
            current_step_id=step_id,
        )
        self.__session.add(saga)
        self.__session.add(saga_step)

    async def get_by_order_id(self, order_id: UUID) -> CreateOrderSagaModel:
        resp = await self.__session.scalars(
            select(CreateOrderSagaModel).where(
                order_id == CreateOrderSagaModel.order_id
            )
        )
        return resp.first()
