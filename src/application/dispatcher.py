import os
import signal
from typing import Any, Awaitable, Callable, Dict, ParamSpec, TypeVar

from src.application.disp_depends import resolve_dependencies
from src.application.ports.logger import ILogger
from src.application.ports.uow import IUnitOfWork
from src.infrastructure.logger.impl import logger
from src.infrastructure.uow.impl import get_uow

P = ParamSpec('P')
R = TypeVar('R')


class BrokerDispatcher:
    def __init__(self, uow: IUnitOfWork, logger: ILogger):
        self.uow = uow
        self.handlers: Dict[str, Callable[..., Awaitable[Any]]] = {}
        self.logger = logger

    def register(
        self, action: str
    ) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
        def wrapper(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
            self.handlers[action] = func
            return func

        return wrapper

    async def dispatch(self, uow: IUnitOfWork, action: str, message: dict[str, Any]) -> None:
        try:
            handler = self.handlers[action]
        except KeyError:
            logger.error(f'Handler for action {action} didnt registered', exc_info=False)
            os.kill(os.getpid(), signal.SIGINT)
            raise
        kwargs = await resolve_dependencies(
            handler,
            provided_kwargs={'uow': uow, 'message': message},
        )
        await handler(**kwargs)


dispatcher = BrokerDispatcher(get_uow(), logger)
