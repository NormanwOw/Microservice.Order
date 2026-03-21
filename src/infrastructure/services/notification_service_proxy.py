from src.application.ports.services import INotificationService
from src.application.ports.uow import IUnitOfWork
from src.config import Settings
from src.domain.commands import NotifyCommand
from src.infrastructure.models import OutboxModel


class NotificationServiceProxy(INotificationService):
    def __init__(self, settings: Settings):
        self.topic = settings.NOTIFICATION_COMMANDS_TOPIC
        self.settings = settings

    async def notify(self, uow: IUnitOfWork, command: NotifyCommand):
        for_outbox = OutboxModel(
            action=command.command_type,
            topic=self.topic,
            payload=command.payload,
            external_reference=command.external_reference.to_dict(),
            producer=self.settings.SERVICE_NAME,
        )
        await uow.outbox.add(for_outbox)
