from src.config import Settings
from src.domain.commands import SendNotifyCommand
from src.infrastructure.models import OutboxModel
from src.infrastructure.services.interfaces import INotificationService
from src.infrastructure.uow.interfaces import IUnitOfWork


class NotificationServiceProxy(INotificationService):
    def __init__(self, uow: IUnitOfWork, settings: Settings):
        self.uow = uow
        self.topic = settings.NOTIFICATION_COMMANDS_TOPIC

    async def notify(self, command: SendNotifyCommand):
        for_outbox = OutboxModel()
        await self.uow.outbox.add(for_outbox)
