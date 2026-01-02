from src.domain.enums import EventTypes, OrderEventTypes
from src.domain.events import (
    FailedCreateOrder,
    OrderCreated,
    OrderPayed,
    PaymentCharged,
)

event_type_mapper = {
    OrderEventTypes.ORDER_CREATED: OrderCreated.__name__,
    OrderEventTypes.ORDER_PAYED: OrderPayed.__name__,
    OrderEventTypes.FAILED_CREATE_ORDER: FailedCreateOrder.__name__,
    EventTypes.PAYMENT_CHARGED: PaymentCharged.__name__,
}
