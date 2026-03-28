from src.application.ports.services import IOrderServiceProxy
from src.application.ports.uow import IUnitOfWork
from src.config import Settings
from src.domain.commands import CancelCommand
from src.infrastructure.models import OutboxModel


class OrderServiceProxy(IOrderServiceProxy):
    def __init__(self, settings: Settings):
        self.topic = settings.ORDER_COMMANDS_TOPIC
        self.settings = settings

    async def compensate(self, uow: IUnitOfWork, command: CancelCommand) -> None:
        for_outbox = OutboxModel(
            action=command.command_type,
            topic=self.topic,
            external_reference=command.external_reference.to_dict()
            if command.external_reference
            else {},
            producer=self.settings.SERVICE_NAME,
            payload=command.payload,
        )
        await uow.outbox.add(for_outbox)
