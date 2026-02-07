import os
import signal
from typing import Awaitable, Callable, Dict

from src.application.disp_depends import resolve_dependencies
from src.infrastructure.logger.impl import logger
from src.infrastructure.logger.interfaces import ILogger
from src.infrastructure.uow.impl import get_uow
from src.infrastructure.uow.interfaces import IUnitOfWork


class BrokerDispatcher:
    def __init__(self, uow: IUnitOfWork, logger: ILogger):
        self.uow = uow
        self.handlers: Dict[str, Callable[[dict], Awaitable[None]]] = {}
        self.logger = logger

    def register(self, action: str):
        def wrapper(func):
            self.handlers[action] = func
            return func

        return wrapper

    async def dispatch(self, uow: IUnitOfWork, action, message: dict):
        try:
            handler = self.handlers[action]
        except KeyError:
            logger.error(f'Handler for action {action} didnt registered', exc_info=False)
            os.kill(os.getpid(), signal.SIGINT)
        kwargs = await resolve_dependencies(
            handler,
            provided_kwargs={'uow': uow, 'message': message},
        )
        await handler(**kwargs)


dispatcher = BrokerDispatcher(get_uow(), logger)
