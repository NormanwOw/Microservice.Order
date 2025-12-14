import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI

from src.config import settings
from src.infrastructure.logger.impl import logger
from src.infrastructure.messaging.consumer import KafkaConsumer
from src.infrastructure.messaging.kafka_router import KafkaMessageRouter
from src.infrastructure.messaging.producer import KafkaProducer
from src.infrastructure.uow.impl import get_uow
from src.presentation.routers.order_router import router as order_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info('Start app...')
    producer = KafkaProducer(settings)
    await producer.start()
    app.state.producer = producer
    consumer = KafkaConsumer(settings)
    asyncio.create_task(KafkaMessageRouter(get_uow(), consumer).run())
    yield
    logger.info('App shutdown')


app = FastAPI(title='Order Service', version='0.0.1', lifespan=lifespan)
app.include_router(order_router)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
