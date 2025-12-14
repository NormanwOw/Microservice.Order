from src.domain.enums import CreateOrderStepStatus, OrderStatus
from src.infrastructure.exceptions import OrderDoesNotExist, SagaDoesNotExist
from src.infrastructure.messaging.messages import OrderMessage
from src.infrastructure.models import CreateOrderSagaStepModel, OrderModel
from src.infrastructure.services.interfaces import IPaymentService
from src.infrastructure.uow.interfaces import IUnitOfWork


class CreateOrderSaga:
    def __init__(
        self,
        uow: IUnitOfWork,
        payment_service_proxy: IPaymentService,
    ):
        self.uow = uow
        self.payment = payment_service_proxy

    async def on_order_created(self, message: OrderMessage):
        async with self.uow:
            await self.uow.create_order_saga.create(message)
            await self.payment.verify(message.order_id)
            await self.uow.commit()

    async def compensate(self, message: OrderMessage):
        async with self.uow:
            saga = await self.uow.create_order_saga.get_by_order_id(message.order_id)

            if not saga:
                raise SagaDoesNotExist

            step = CreateOrderSagaStepModel(
                saga_id=saga.id,
                event_type=OrderStatus.FAILED,
                status=CreateOrderStepStatus.IN_PROGRESS,
                payload=message.model_dump(),
            )
            await self.uow.create_order_saga_step.add(step)

            order = await self.uow.orders.find_one(
                OrderModel.id,
                message.order_id,
            )
            if not order:
                raise OrderDoesNotExist

            await self.payment.cancel(order)

            step.status = CreateOrderStepStatus.COMPENSATED
            saga.state = OrderStatus.FAILED

            await self.uow.commit()
