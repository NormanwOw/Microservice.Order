from typing import Awaitable, Callable, Dict

from src.infrastructure.logger.impl import logger
from src.infrastructure.logger.interfaces import ILogger
from src.infrastructure.messaging.messages import OrderMessage


class EventDispatcher:
    def __init__(self, logger: ILogger):
        self.logger = logger
        self._handlers: Dict[str, Callable[[OrderMessage], Awaitable[None]]] = {}

    def register(self, event_type: str):
        def wrapper(func):
            self._handlers[event_type] = func
            return func

        return wrapper

    async def dispatch(self, message: OrderMessage):
        handler = self._handlers.get(message.event_type)
        if handler is None:
            return

        await handler(message)


dispatcher = EventDispatcher(logger)
