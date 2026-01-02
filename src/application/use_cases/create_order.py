from src.config import Settings
from src.domain.aggregates import Order
from src.domain.commands import CreateOrderCommand, ExternalReference, ReserveProductsCommand
from src.domain.exceptions import OrderAlreadyExists
from src.infrastructure.services.interfaces import IStocksServiceProxy
from src.infrastructure.uow.interfaces import IUnitOfWork
from src.presentation.schemas import CreateOrderResponse


class CreateOrder:
    def __init__(
        self, uow: IUnitOfWork, stocks_service_proxy: IStocksServiceProxy, settings: Settings
    ):
        self.uow = uow
        self.stocks_service = stocks_service_proxy
        self.settings = settings

    async def __call__(self, command: CreateOrderCommand) -> CreateOrderResponse:
        async with self.uow:
            order = await self.uow.orders.load(
                order_id=command.order_id,
            )

            if order is not None:
                raise OrderAlreadyExists

            order = Order()
            events = order.decide(command)

            await self.uow.orders.append_events(
                order_id=command.order_id,
                expected_version=0,
                events=events,
            )

            for event in events:
                order.apply(event)

            await self.uow.orders.upsert_projection(order, command.customer_id)
            await self.uow.create_order_saga.start(order, command.customer_id)
            command = ReserveProductsCommand(
                products=command.products,
                external_reference=ExternalReference(**order.model_dump()),
            )
            await self.stocks_service.reserve_products(command)
            await self.uow.commit()

            return CreateOrderResponse(order_id=order.id)
