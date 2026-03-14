from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repositories import ICreateOrderSagaRepository
from src.domain.aggregates import Order
from src.domain.enums import CreateOrderSagaStatus, CreateOrderStepStatus, OrderEventTypes
from src.infrastructure.models import CreateOrderSagaModel, CreateOrderSagaStepModel
from src.infrastructure.repositories.base_repository import SQLAlchemyRepository


class CreateOrderSagaRepository(SQLAlchemyRepository, ICreateOrderSagaRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, CreateOrderSagaModel)

    async def start(self, saga_id: UUID, order: Order, customer_id: UUID):
        step_id = uuid4()
        payload = {
            'customer_id': str(customer_id),
            'products': [product.to_dict() for product in order.products],
        }
        self.__session.add(
            CreateOrderSagaStepModel(
                id=step_id,
                saga_id=saga_id,
                event_type=OrderEventTypes.ORDER_CREATED,
                status=CreateOrderStepStatus.SUCCESS,
                payload=payload,
            )
        )
        self.__session.add(
            CreateOrderSagaModel(
                id=saga_id,
                order_id=order.id,
                state=CreateOrderSagaStatus.STARTED,
                order_version=order.version,
                current_step_id=step_id,
                context=payload,
            )
        )
