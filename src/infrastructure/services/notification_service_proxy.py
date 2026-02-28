from src.config import Settings
from src.domain.commands import SendSuccessCreatedOrderNotifyCommand
from src.infrastructure.models import OutboxModel
from src.infrastructure.services.interfaces import INotificationService
from src.infrastructure.uow.interfaces import IUnitOfWork


class NotificationServiceProxy(INotificationService):
    def __init__(self, settings: Settings):
        self.topic = settings.NOTIFICATION_COMMANDS_TOPIC
        self.producer = 'order-service'

    async def notify_success_created_order(
        self, uow: IUnitOfWork, command: SendSuccessCreatedOrderNotifyCommand
    ):
        for_outbox = OutboxModel(
            action=command.command_type,
            topic=self.topic,
            payload=command.payload.to_dict(),
            external_reference=command.external_reference.to_dict(),
            producer=self.producer,
        )
        await uow.outbox.add(for_outbox)
