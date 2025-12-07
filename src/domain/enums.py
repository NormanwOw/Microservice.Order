from enum import Enum


class OrderStatus(str, Enum):
    ORDER_CREATED = "ORDER_CREATED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAYMENT_COMPLETED = "PAYMENT_COMPLETED"
    NOTIFICATION_SENT = "NOTIFICATION_SENT"
    ANALYTIC_RECORDED = "ANALYTIC_RECORDED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Currency(str, Enum):
    USD = "$"
    EUR = "€"


class CreateOrderStepStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
