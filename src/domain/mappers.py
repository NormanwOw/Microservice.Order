from src.domain.enums import EventTypes, OrderEventTypes
from src.domain.events import (
    FailedCreateOrder,
    OrderCreated,
    PaymentCharged,
    ProductsCommitted,
    ProductsReserved,
)

event_type_mapper = {
    OrderEventTypes.ORDER_CREATED: OrderCreated,
    OrderEventTypes.PAYMENT_CHARGED: PaymentCharged,
    OrderEventTypes.FAILED_CREATE_ORDER: FailedCreateOrder,
    EventTypes.PRODUCTS_RESERVED: ProductsReserved,
    EventTypes.PRODUCTS_COMMITTED: ProductsCommitted,
}
