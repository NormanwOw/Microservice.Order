from src.config import Settings
from src.infrastructure.services.interfaces import IPaymentService
from src.infrastructure.uow.interfaces import IUnitOfWork


class PaymentServiceProxy(IPaymentService):
    def __init__(self, uow: IUnitOfWork, settings: Settings):
        self.uow = uow
        self.topic = settings.PAYMENT_EVENTS_TOPIC
