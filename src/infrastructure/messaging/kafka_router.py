import asyncio

from sqlalchemy.exc import IntegrityError

from src.application.dispatcher import dispatcher
from src.infrastructure.messaging.interfaces import IKafkaConsumer
from src.infrastructure.messaging.messages import EventMessage
from src.infrastructure.models import ProcessedMessagesModel
from src.infrastructure.uow.interfaces import IUnitOfWork


class KafkaMessageRouter:
    def __init__(self, uow: IUnitOfWork, consumer: IKafkaConsumer):
        self.uow = uow
        self.consumer = consumer

    async def run(self):
        await self.consumer.start()
        try:
            while True:
                async for msg in self.consumer:
                    message_schema = EventMessage(**msg.value)

                    async with self.uow:
                        try:
                            await self.uow.processed_messages.add(
                                ProcessedMessagesModel(id=message_schema.message_id)
                            )
                        except IntegrityError:
                            await self.consumer.commit()
                            continue

                        await dispatcher.dispatch(
                            event_type=message_schema.event_type,
                            message=msg.value,
                        )

                        await self.uow.commit()
                        await self.consumer.commit()

                await asyncio.sleep(0.2)
        finally:
            await self.consumer.stop()
