import json

from aiokafka import AIOKafkaProducer
from pydantic import BaseModel

from common.config import settings
from common.logger.impl import logger
from common.logger.interfaces import ILogger


class Producer:
    def __init__(self, settings, logger: ILogger):
        self.settings = settings
        self.logger = logger
        self.producer: AIOKafkaProducer | None = None

    async def start(self):
        if not self.producer:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.settings.KAFKA_HOSTS,
                request_timeout_ms=30000,
                retry_backoff_ms=1000,
            )
            try:
                await self.producer.start()
                self.logger.info("Kafka producer started")
            except Exception:
                self.logger.error("Failed to start producer")
                raise

    async def send_message(self, message: BaseModel, topic: str, partition: int = 0):
        if not self.producer:
            await self.start()

        await self.producer.send(
            topic=topic,
            value=json.dumps(message.model_dump()).encode("utf-8"),
            partition=partition,
        )
        self.logger.info(f"Committed message ID={message.message_id}")


producer = Producer(settings, logger)
