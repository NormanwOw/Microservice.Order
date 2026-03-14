from src.application.ports.uow import IUnitOfWork
from src.infrastructure.messaging.messages import CancelOrderMessage
from src.infrastructure.models import OrderModel


class CancelOrder:
    async def __call__(self, uow: IUnitOfWork, message: CancelOrderMessage):
        await uow.orders.update(
            {'status': message.payload['status']}, OrderModel.id, message.external_reference.id
        )
