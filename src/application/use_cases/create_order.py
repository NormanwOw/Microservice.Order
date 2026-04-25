import uuid

from src.application.ports.logger import ILogger
from src.application.ports.services import IStocksServiceProxy
from src.application.ports.uow import IUnitOfWork
from src.config import Settings
from src.domain.aggregates import Order
from src.domain.commands import CreateOrderCommand, ExternalReference, ReserveProductsCommand
from src.domain.enums import AggregateType, CommandTypes, ServiceName
from src.domain.events import StepCompleted
from src.domain.exceptions import OrderAlreadyExists
from src.presentation.schemas import CreateOrderResponse


class CreateOrder:
    def __init__(
        self,
        uow: IUnitOfWork,
        stocks_service_proxy: IStocksServiceProxy,
        settings: Settings,
        logger: ILogger,
    ):
        self.uow = uow
        self.stocks_service = stocks_service_proxy
        self.settings = settings
        self.logger = logger

    async def __call__(self, command: CreateOrderCommand) -> CreateOrderResponse:
        async with self.uow:
            order = await self.uow.orders.load(
                order_id=command.order_id,
            )

            if order is not None:
                raise OrderAlreadyExists

            order = Order(products=[])
            saga_id = uuid.uuid4()

            external_reference = ExternalReference(
                id=command.order_id, type=AggregateType.ORDER, version=1
            )
            reserve_command = ReserveProductsCommand(
                products=command.products,
                external_reference=external_reference,
            )
            event = StepCompleted(
                saga_id=saga_id,
                service=ServiceName.ORDER,
                command_type=CommandTypes.CREATE_ORDER,
                command_payload={
                    'products': [product.to_dict() for product in command.products],
                    'external_reference': external_reference.to_dict(),
                },
                compensation_command_type=CommandTypes.CANCEL_ORDER,
                compensation_payload={},
            )
            order.apply(event)
            await self.uow.create_order_saga.start(saga_id, order, command.customer_id)
            await self.uow.orders.upsert_projection(order, command.customer_id)

            await self.uow.orders.append_events(
                order_id=command.order_id,
                expected_version=0,
                events=[event],
            )
            await self.stocks_service.reserve_products(self.uow, reserve_command)
            await self.uow.commit()
            self.logger.info(
                f'Order {order.id} created. Products: {command.products}. '
                f'Customer: {command.customer_id}'
            )
            return CreateOrderResponse(order_id=order.id or uuid.uuid4())
