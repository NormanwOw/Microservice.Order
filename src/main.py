import traceback
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.infrastructure.logger.impl import logger
from src.presentation.exception_mapper import exceptions_mapper
from src.presentation.routers.order_router import router as order_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info('Start app...')
    yield
    logger.info('App shutdown')


app = FastAPI(title='Order Service', version='0.0.1', lifespan=lifespan)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except tuple(exceptions_mapper.keys()) as ex:
            http_exc = exceptions_mapper[type(ex)]
            return JSONResponse(
                status_code=http_exc.status_code, content={'detail': http_exc.detail}
            )
        except Exception as exc:
            tb_str = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logger.error(f'Exception during request: {exc}\nTraceback:\n{tb_str}')
            raise


app.add_middleware(LoggingMiddleware)

app.include_router(order_router)
