import json

from aiokafka import AIOKafkaConsumer

from src.application.ports.broker import IKafkaConsumer
from src.config import Settings


class KafkaConsumer(IKafkaConsumer, AIOKafkaConsumer):
    def __init__(self, settings: Settings):
        super().__init__(
            settings.SAGA_EVENTS_TOPIC,
            bootstrap_servers=settings.KAFKA_HOSTS,
            group_id='order_group',
            enable_auto_commit=False,
            auto_offset_reset='earliest',
            value_deserializer=lambda msg: json.loads(msg.decode()),
        )
