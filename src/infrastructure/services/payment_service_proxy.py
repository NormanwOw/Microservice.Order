from uuid import UUID, uuid4

from src.config import Settings
from src.infrastructure.models import OutboxModel
from src.infrastructure.services.interfaces import IPaymentService
from src.infrastructure.uow.interfaces import IUnitOfWork


class PaymentServiceProxy(IPaymentService):
    def __init__(self, uow: IUnitOfWork, settings: Settings):
        self.uow = uow
        self.topic = settings.PAYMENT_EVENTS_TOPIC

    async def verify(self, order_id: UUID):
        for_outbox = OutboxModel(
            topic=self.topic,
            message={
                'message_id': str(uuid4()),
                'order_id': str(order_id),
                'event_type': 'VERIFY_PAYMENT',
            },
        )
        await self.uow.outbox.add(for_outbox)

    async def cancel(self, order_id: UUID):
        for_outbox = OutboxModel(
            topic=self.topic,
            message={
                'message_id': str(uuid4()),
                'order_id': str(order_id),
                'event_type': 'CANCEL_PAYMENT',
            },
        )
        await self.uow.outbox.add(for_outbox)
