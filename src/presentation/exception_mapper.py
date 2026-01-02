from fastapi import HTTPException

from src.domain import exceptions as d_exc

exceptions_mapper = {
    d_exc.EventNotSupported: HTTPException(status_code=400, detail='Event not supported'),
}
