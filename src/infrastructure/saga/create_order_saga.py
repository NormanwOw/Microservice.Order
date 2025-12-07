import asyncio

from sqlalchemy.exc import IntegrityError

from src.infrastructure.messaging.interfaces import IKafkaConsumer
from src.infrastructure.messaging.messages import Message
from src.infrastructure.models import ProcessedMessagesModel
from src.infrastructure.saga.dispatcher import dispatcher
from src.infrastructure.uow.interfaces import IUnitOfWork


class CreateOrderSaga:
    def __init__(self, uow: IUnitOfWork, kafka_consumer: IKafkaConsumer):
        self.uow = uow
        self.consumer = kafka_consumer

    async def __call__(self):
        await self.consumer.start()
        try:
            while True:
                async for message in self.consumer:
                    message_schema = Message(**message.value)
                    if message_schema:
                        async with self.uow:
                            try:
                                await self.uow.processed_messages.add(
                                    ProcessedMessagesModel(id=message_schema.message_id)
                                )
                                await self.uow.commit()
                            except IntegrityError:
                                await self.consumer.commit()
                                continue

                            await dispatcher.dispatch(message)
                            await self.consumer.commit()
                            await self.uow.commit()

                await asyncio.sleep(0.5)

        finally:
            await self.consumer.stop()
