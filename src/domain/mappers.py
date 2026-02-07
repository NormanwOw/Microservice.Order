from src.domain.enums import EventTypes, OrderEventTypes
from src.domain.events import (
    FailedCreateOrder,
    OrderCreated,
    OrderPayed,
    ProductsReserved,
)

event_type_mapper = {
    OrderEventTypes.ORDER_CREATED: OrderCreated,
    OrderEventTypes.ORDER_PAYED: OrderPayed,
    OrderEventTypes.FAILED_CREATE_ORDER: FailedCreateOrder,
    EventTypes.PRODUCTS_RESERVED: ProductsReserved,
}
