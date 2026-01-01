from typing import Awaitable, Callable, Dict

from src.application.disp_depends import resolve_dependencies
from src.infrastructure.logger.impl import logger
from src.infrastructure.logger.interfaces import ILogger
from src.infrastructure.models import ProcessedMessagesModel
from src.infrastructure.uow.impl import get_uow
from src.infrastructure.uow.interfaces import IUnitOfWork


class EventDispatcher:
    def __init__(self, uow: IUnitOfWork, logger: ILogger):
        self.uow = uow
        self.handlers: Dict[str, Callable[[dict], Awaitable[None]]] = {}
        self.logger = logger

    def register(self, event_type: str):
        def wrapper(func):
            self.handlers[event_type] = func
            return func

        return wrapper

    async def dispatch(self, event_type, message: dict):
        handler = self.handlers[event_type]
        kwargs = await resolve_dependencies(
            handler,
            provided_kwargs={'message': message},
        )
        async with self.uow:
            is_message_processed = await self.uow.processed_messages.find_one(
                ProcessedMessagesModel.id, message['message_id']
            )
            if is_message_processed:
                return
        try:
            await handler(**kwargs)
            async with self.uow:
                await self.uow.processed_messages.add(
                    ProcessedMessagesModel(id=message['message_id'])
                )
                await self.uow.commit()
        except Exception:
            self.logger.error(f'Error while dispatching event {event_type}, message {message}')


dispatcher = EventDispatcher(get_uow(), logger)
