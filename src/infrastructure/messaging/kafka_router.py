import asyncio

from sqlalchemy.exc import IntegrityError
from tenacity import AsyncRetrying, RetryError, stop_after_attempt, wait_fixed

from src.application.dispatcher import dispatcher
from src.infrastructure.logger.interfaces import ILogger
from src.infrastructure.messaging.interfaces import IKafkaConsumer
from src.infrastructure.messaging.messages import EventMessage
from src.infrastructure.models import ProcessedMessagesModel
from src.infrastructure.uow.interfaces import IUnitOfWork


class KafkaMessageRouter:
    def __init__(self, uow: IUnitOfWork, consumer: IKafkaConsumer, logger: ILogger):
        self.uow = uow
        self.consumer = consumer
        self.logger = logger

    async def run(self):
        await self.consumer.start()
        try:
            while True:
                async for msg in self.consumer:
                    message_schema = EventMessage(**msg.value, event_type=msg.value['action'])

                    async with self.uow:
                        try:
                            await self.uow.processed_messages.add(
                                ProcessedMessagesModel(id=message_schema.message_id)
                            )
                        except IntegrityError:
                            await self.consumer.commit()
                            self.logger.info(
                                f'Skipped already processed message ' f'{message_schema.message_id}'
                            )
                            continue

                        try:
                            async for attempt in AsyncRetrying(
                                stop=stop_after_attempt(3), wait=wait_fixed(2)
                            ):
                                with attempt:
                                    await dispatcher.dispatch(
                                        uow=self.uow,
                                        action=message_schema.event_type,
                                        message=msg.value,
                                    )
                                    await self.uow.commit()
                        except RetryError:
                            self.logger.error(
                                f'Error while process message: '
                                f'{message_schema.message_id} | Message: {msg.value}'
                            )
                            await self.uow.rollback()
                            await self.uow.processed_messages.add(
                                ProcessedMessagesModel(id=message_schema.message_id)
                            )
                            await self.uow.commit()
                        finally:
                            await self.consumer.commit()

                await asyncio.sleep(1)
        finally:
            await self.consumer.stop()
