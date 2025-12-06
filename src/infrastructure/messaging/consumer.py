import json

from aiokafka import AIOKafkaConsumer

from src.config import Settings
from src.infrastructure.messaging.messages import OrderMessage


class KafkaConsumer(AIOKafkaConsumer):
    def __init__(self, settings: Settings):
        super().__init__(
            settings.SAGA_ORDER_EVENTS_TOPIC,
            bootstrap_servers=settings.KAFKA_HOSTS,
            group_id="order_group",
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            value_deserializer=lambda msg: OrderMessage(**json.loads(msg.decode())),
        )
