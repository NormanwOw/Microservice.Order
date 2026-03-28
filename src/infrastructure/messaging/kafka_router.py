import asyncio
from typing import Union

from sqlalchemy.exc import IntegrityError
from tenacity import AsyncRetrying, RetryError, stop_after_attempt, wait_fixed

from src.application.dispatcher import dispatcher
from src.application.ports.broker import IKafkaConsumer
from src.application.ports.logger import ILogger
from src.application.ports.uow import IUnitOfWork
from src.config import settings
from src.domain.enums import OrderEventTypes
from src.infrastructure.messaging.messages import CommandMessage, EventMessage
from src.infrastructure.models import ProcessedMessagesModel


class KafkaMessageRouter:
    def __init__(self, uow: IUnitOfWork, consumer: IKafkaConsumer, logger: ILogger):
        self.uow = uow
        self.consumer = consumer
        self.logger = logger

    async def run(self) -> None:
        await self.consumer.start()
        try:
            message_schema: Union[EventMessage, CommandMessage]
            while True:
                try:
                    async for msg in self.consumer:
                        if msg.value['action'] in OrderEventTypes:
                            message_schema = EventMessage(**msg.value)
                        else:
                            message_schema = CommandMessage(**msg.value)

                        if not settings.DEBUG:
                            async with self.uow:
                                try:
                                    await self.uow.processed_messages.add(
                                        ProcessedMessagesModel(id=message_schema.message_id)
                                    )
                                    await self.uow.commit()
                                except IntegrityError:
                                    await self.consumer.commit()
                                    self.logger.info(
                                        f'Skipped already processed message '
                                        f'{message_schema.message_id}'
                                    )
                                    continue

                        async with self.uow:
                            try:
                                async for attempt in AsyncRetrying(
                                    stop=stop_after_attempt(3), wait=wait_fixed(2)
                                ):
                                    with attempt:
                                        try:
                                            await dispatcher.dispatch(
                                                uow=self.uow,
                                                action=message_schema.action,
                                                message=msg.value,
                                            )
                                            await self.uow.commit()
                                            await self.consumer.commit()
                                        except Exception:
                                            await self.uow.rollback()
                                            raise
                            except RetryError:
                                self.logger.error(
                                    f'Error while process message: '
                                    f'{message_schema.message_id} | Message: {msg.value}'
                                )

                                await self.uow.processed_messages.delete_one(
                                    ProcessedMessagesModel.id, message_schema.message_id
                                )
                                await self.uow.commit()
                except Exception:
                    self.logger.error('Unexpected error')
                    await asyncio.sleep(60)
                await asyncio.sleep(1)
        finally:
            await self.consumer.stop()
