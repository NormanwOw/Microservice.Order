from enum import Enum


class OrderEventTypes(str, Enum):
    ORDER_CREATED = 'OrderCreated'
    ORDER_INITIALIZED = 'OrderInitialized'
    ORDER_PAYED = 'OrderPayed'
    FAILED_CREATE_ORDER = 'FailedCreateOrder'


class EventTypes(str, Enum):
    PAYMENT_CHARGED = 'PaymentCharged'


class CommandTypes(str, Enum):
    SEND_NOTIFY = 'SendNotify'
    RESERVE_PRODUCTS = 'ReserveProducts'
    CREATE_ORDER = 'CreateOrder'


class Currency(str, Enum):
    USD = 'USD'
    EUR = 'EUR'


class CreateOrderStepStatus(str, Enum):
    SUCCESS = 'SUCCESS'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPENSATED = 'COMPENSATED'
    FAILED = 'FAILED'


class CreateOrderSagaStatus(str, Enum):
    STARTED = 'STARTED'
    WAITING_PAYMENT = 'WAITING_PAYMENT'
    PAYMENT_COMPLETED = 'PAYMENT_COMPLETED'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'


class AggregateTypes(str, Enum):
    ORDER = 'order'


class MessageType(str, Enum):
    EVENT = 'event'
    COMMAND = 'command'
