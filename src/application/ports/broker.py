from abc import ABC

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer  # type: ignore


class IKafkaConsumer(AIOKafkaConsumer, ABC): ...  # type: ignore


class IKafkaProducer(AIOKafkaProducer, ABC): ...  # type: ignore
