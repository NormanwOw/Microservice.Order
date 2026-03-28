from fastapi import APIRouter

from src.config import VERSION

router = APIRouter(prefix=f'/api/v{VERSION}', tags=['Main'])


@router.get('/healthy')
def health_check() -> dict[str, str]:
    return {'status': 'ok'}
