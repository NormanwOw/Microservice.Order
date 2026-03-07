from src.application.ports.services import INotificationService
from src.application.ports.uow import IUnitOfWork
from src.config import Settings
from src.domain.commands import SendSuccessCreatedOrderNotifyCommand
from src.infrastructure.models import OutboxModel


class NotificationServiceProxy(INotificationService):
    def __init__(self, settings: Settings):
        self.topic = settings.NOTIFICATION_COMMANDS_TOPIC
        self.settings = settings

    async def notify_success_created_order(
        self, uow: IUnitOfWork, command: SendSuccessCreatedOrderNotifyCommand
    ):
        for_outbox = OutboxModel(
            action=command.command_type,
            topic=self.topic,
            payload=command.payload.to_dict(),
            external_reference=command.external_reference.to_dict(),
            producer=self.settings.SERVICE_NAME,
        )
        await uow.outbox.add(for_outbox)
