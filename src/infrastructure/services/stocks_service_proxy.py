from src.config import Settings
from src.domain.commands import ReserveProductsCommand
from src.domain.enums import CommandTypes
from src.infrastructure.models import OutboxModel
from src.infrastructure.services.interfaces import IStocksServiceProxy
from src.infrastructure.uow.interfaces import IUnitOfWork


class StocksServiceProxy(IStocksServiceProxy):
    def __init__(self, uow: IUnitOfWork, settings: Settings):
        self.uow = uow
        self.topic = settings.STOCKS_COMMANDS_TOPIC

    async def reserve_products(self, command: ReserveProductsCommand):
        for_outbox = OutboxModel(
            action=CommandTypes.RESERVE_PRODUCTS,
            topic=self.topic,
            external_reference=command.external_reference.to_dict(),
            payload=[product.to_dict() for product in command.products],
        )
        await self.uow.outbox.add(for_outbox)
