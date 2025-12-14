from typing import Awaitable, Callable, Dict

from src.application.disp_depends import resolve_dependencies
from src.infrastructure.logger.impl import logger
from src.infrastructure.logger.interfaces import ILogger


class EventDispatcher:
    def __init__(self, logger: ILogger):
        self.logger = logger
        self._handlers: Dict[str, Callable[[dict], Awaitable[None]]] = {}

    def register(self, event_type: str):
        def wrapper(func):
            self._handlers[event_type] = func
            return func

        return wrapper

    async def dispatch(self, event_type, message: dict):
        handler = self._handlers[event_type]
        kwargs = await resolve_dependencies(
            handler,
            provided_kwargs={'message': message},
        )
        await handler(**kwargs)


dispatcher = EventDispatcher(logger)
