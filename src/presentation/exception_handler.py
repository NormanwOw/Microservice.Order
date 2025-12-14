from functools import wraps

from fastapi import HTTPException

from src.domain import exceptions as domain_exc


def exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except domain_exc.ProductsDoesNotExists:
            raise HTTPException(status_code=404, detail='Products does not exists')

    return wrapper
