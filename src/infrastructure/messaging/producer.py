from aiokafka import AIOKafkaProducer

from src.config import Settings


class KafkaProducer(AIOKafkaProducer):
    def __init__(self, settings: Settings):
        super().__init__(
            bootstrap_servers=settings.KAFKA_HOSTS,
            value_serializer=lambda msg: msg.model_dump_json().encode("utf-8"),
        )
