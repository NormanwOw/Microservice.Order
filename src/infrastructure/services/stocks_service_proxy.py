from src.application.ports.services import IStocksServiceProxy
from src.application.ports.uow import IUnitOfWork
from src.config import Settings
from src.domain.commands import CommitProductsCommand, ReserveProductsCommand
from src.infrastructure.models import OutboxModel


class StocksServiceProxy(IStocksServiceProxy):
    def __init__(self, settings: Settings):
        self.topic = settings.STOCKS_COMMANDS_TOPIC
        self.settings = settings

    async def reserve_products(self, uow: IUnitOfWork, command: ReserveProductsCommand):
        for_outbox = OutboxModel(
            action=command.command_type,
            topic=self.topic,
            external_reference=command.external_reference.to_dict(),
            producer=self.settings.SERVICE_NAME,
            payload={'products': [product.to_dict() for product in command.products]},
        )
        await uow.outbox.add(for_outbox)

    async def commit_products(self, uow: IUnitOfWork, command: CommitProductsCommand):
        for_outbox = OutboxModel(
            action=command.command_type,
            topic=self.topic,
            external_reference=command.external_reference.to_dict(),
            producer=self.settings.SERVICE_NAME,
            payload={'products': [product.to_dict() for product in command.products]},
        )
        await uow.outbox.add(for_outbox)
