from src.infrastructure.repositories.create_order_saga_repository import (
    CreateOrderSagaRepository,
)
from src.infrastructure.repositories.create_order_saga_step_repository import (
    CreateOrderSagaStepRepository,
)
from src.infrastructure.repositories.customer_repository import CustomerRepository
from src.infrastructure.repositories.interfaces import (
    ICreateOrderSagaRepository,
    ICreateOrderSagaStepRepository,
    ICustomerRepository,
    IOrderEventRepository,
    IOrderItemRepository,
    IOrderRepository,
    IOutboxRepository,
    IProcessedMessagesModelRepository,
    IProductRepository,
)
from src.infrastructure.repositories.order_event_repository import OrderEventRepository
from src.infrastructure.repositories.order_item_repository import OrderItemRepository
from src.infrastructure.repositories.order_repository import OrderRepository
from src.infrastructure.repositories.outbox_repository import OutboxRepository
from src.infrastructure.repositories.processed_message_repository import (
    ProcessedMessagesModelRepository,
)
from src.infrastructure.repositories.product_repository import ProductRepository
from src.infrastructure.session import async_session
from src.infrastructure.uow.interfaces import IUnitOfWork


class UnitOfWork(IUnitOfWork):
    def __init__(self, session_factory):
        self.__session_factory = session_factory

    async def __aenter__(self):
        self.__session = self.__session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            await self.rollback()
        await self.__session.close()

    async def commit(self):
        await self.__session.commit()

    async def rollback(self):
        await self.__session.rollback()

    @property
    def products(self) -> IProductRepository:
        return ProductRepository(self.__session)

    @property
    def outbox(self) -> IOutboxRepository:
        return OutboxRepository(self.__session)

    @property
    def processed_messages(self) -> IProcessedMessagesModelRepository:
        return ProcessedMessagesModelRepository(self.__session)

    @property
    def orders(self) -> IOrderRepository:
        return OrderRepository(self.__session)

    @property
    def order_items(self) -> IOrderItemRepository:
        return OrderItemRepository(self.__session)

    @property
    def create_order_saga(self) -> ICreateOrderSagaRepository:
        return CreateOrderSagaRepository(self.__session)

    @property
    def create_order_saga_step(self) -> ICreateOrderSagaStepRepository:
        return CreateOrderSagaStepRepository(self.__session)

    @property
    def customers(self) -> ICustomerRepository:
        return CustomerRepository(self.__session)

    @property
    def order_events(self) -> IOrderEventRepository:
        return OrderEventRepository(self.__session)


def get_uow() -> IUnitOfWork:
    return UnitOfWork(session_factory=async_session)
