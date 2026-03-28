from src.application.ports.services import IPaymentService
from src.application.ports.uow import IUnitOfWork
from src.config import Settings
from src.domain.commands import CancelCommand, ChargePaymentCommand
from src.infrastructure.models import OutboxModel


class PaymentServiceProxy(IPaymentService):
    def __init__(self, settings: Settings):
        self.topic = settings.PAYMENT_COMMANDS_TOPIC
        self.settings = settings

    async def charge_payment(self, uow: IUnitOfWork, command: ChargePaymentCommand) -> None:
        for_outbox = OutboxModel(
            action=command.command_type,
            topic=self.topic,
            external_reference=command.external_reference.to_dict()
            if command.external_reference
            else {},
            producer=self.settings.SERVICE_NAME,
            payload=command.payload.to_dict(),
        )
        await uow.outbox.add(for_outbox)

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
