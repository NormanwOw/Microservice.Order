from src.config import Settings
from src.domain.commands import ReserveProductsCommand
from src.domain.enums import AggregateTypes, CommandTypes, MessageType
from src.infrastructure.models import OutboxModel
from src.infrastructure.services.interfaces import IStocksServiceProxy
from src.infrastructure.uow.interfaces import IUnitOfWork


class StocksServiceProxy(IStocksServiceProxy):
    def __init__(self, uow: IUnitOfWork, settings: Settings):
        self.uow = uow
        self.topic = settings.STOCKS_COMMANDS_TOPIC

    async def reserve_products(self, command: ReserveProductsCommand):
        for_outbox = OutboxModel(
            aggregate_type=AggregateTypes.ORDER,
            aggregate_id=command.external_reference.id,
            name=CommandTypes.RESERVE_PRODUCTS,
            type=MessageType.COMMAND,
            aggregate_version=command.external_reference.version,
            topic=self.topic,
            payload=[product.to_dict() for product in command.products],
        )
        await self.uow.outbox.add(for_outbox)
