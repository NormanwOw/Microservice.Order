from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from common.logger.impl import logger


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncIterator[None]:
    logger.info("Start app...")
    yield
    logger.info("App shutdown")


app = FastAPI(title="Order Service", version="0.0.1", lifespan=lifespan)
