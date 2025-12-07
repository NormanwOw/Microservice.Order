from src.domain.enums import OrderStatus
from src.infrastructure.logger.impl import logger
from src.infrastructure.messaging.messages import OrderMessage
from src.infrastructure.saga.dispatcher import dispatcher


@dispatcher.register(OrderStatus.FAILED)
async def handle_cancel_order(message: dict):
    message = OrderMessage(**message)
    logger.info(f"[ORDER] Cancel order={message.order_id}")
