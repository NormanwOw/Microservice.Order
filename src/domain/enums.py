from enum import Enum


class OrderEventTypes(str, Enum):
    ORDER_CREATED = 'OrderCreated'
    ORDER_INITIALIZED = 'OrderInitialized'
    PRODUCTS_RESERVED = 'ProductsReserved'
    PRODUCTS_COMMITTED = 'ProductsCommitted'
    PAYMENT_CHARGED = 'PaymentCharged'
    NOTIFIED_CUSTOMER_SUCCESS_ORDER_CREATED = 'NotifiedCustomerSuccessOrderCreated'
    FAILED_CREATE_ORDER = 'FailedCreateOrder'


class EventTypes(str, Enum):
    PRODUCTS_RESERVED = 'ProductsReserved'
    PRODUCTS_COMMITTED = 'ProductsCommitted'
    PAYMENT_CHARGED = 'PaymentCharged'

    CHARGE_PAYMENT_FAILED = 'ChargePaymentFailed'
    COMMIT_FAILED = 'CommitFailed'
    RESERVE_FAILED = 'ReserveFailed'


class CommandTypes(str, Enum):
    CHARGE_PAYMENT = 'ChargePayment'
    SEND_SUCCESS_CREATED_ORDER_NOTIFY = 'SendSuccessCreatedOrderNotify'
    RESERVE_PRODUCTS = 'ReserveProducts'
    COMMIT_PRODUCTS = 'CommitProducts'
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
    WAITING_PRODUCTS_COMMITTED = 'WAITING_PRODUCTS_COMMITTED'
    WAITING_NOTIFY_ORDER_COMPLETED = 'WAITING_NOTIFY_ORDER_COMPLETED'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'


class AggregateType(str, Enum):
    ORDER = 'order'


class MessageType(str, Enum):
    EVENT = 'event'
    COMMAND = 'command'


class Services(str, Enum):
    ORDER = 'order-service'
    PAYMENT = 'payment-service'
    STOCKS = 'stocks-service'
    NOTIFICATION = 'notification-service'
