from src.config import Settings
from src.domain.commands import ChargePaymentCommand
from src.infrastructure.models import OutboxModel
from src.infrastructure.services.interfaces import IPaymentService
from src.infrastructure.uow.interfaces import IUnitOfWork


class PaymentServiceProxy(IPaymentService):
    def __init__(self, settings: Settings):
        self.topic = settings.PAYMENT_COMMANDS_TOPIC

    async def charge_payment(self, uow: IUnitOfWork, command: ChargePaymentCommand):
        for_outbox = OutboxModel(
            action=command.command_type,
            topic=self.topic,
            external_reference=command.external_reference.to_dict(),
            producer='order-service',
            payload=command.payload.to_dict(),
        )
        await uow.outbox.add(for_outbox)
