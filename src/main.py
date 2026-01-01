from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from src.infrastructure.logger.impl import logger
from src.presentation.routers.order_router import router as order_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info('Start app...')
    yield
    logger.info('App shutdown')


app = FastAPI(title='Order Service', version='0.0.1', lifespan=lifespan)
app.include_router(order_router)
