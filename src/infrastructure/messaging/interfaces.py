from abc import ABC

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer


class IKafkaConsumer(AIOKafkaConsumer, ABC): ...


class IKafkaProducer(AIOKafkaProducer, ABC): ...
