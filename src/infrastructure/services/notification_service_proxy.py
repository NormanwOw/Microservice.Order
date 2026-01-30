from src.config import Settings
from src.domain.commands import SendNotifyCommand
from src.infrastructure.models import OutboxModel
from src.infrastructure.services.interfaces import INotificationService
from src.infrastructure.uow.interfaces import IUnitOfWork


class NotificationServiceProxy(INotificationService):
    def __init__(self, settings: Settings):
        self.topic = settings.NOTIFICATION_COMMANDS_TOPIC

    async def notify(self, uow: IUnitOfWork, command: SendNotifyCommand):
        for_outbox = OutboxModel()
        await uow.outbox.add(for_outbox)
