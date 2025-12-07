from src.domain.enums import OrderStatus
from src.infrastructure.logger.impl import logger
from src.infrastructure.messaging.messages import OrderMessage
from src.infrastructure.saga.dispatcher import dispatcher


@dispatcher.register(OrderStatus.ORDER_CREATED)
async def handle_create_order(message: dict):
    message = OrderMessage(**message)
    logger.info(f"[ORDER] Creating order={message.order_id})")
