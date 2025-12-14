from src.application.use_cases.get_products import GetProducts
from src.infrastructure.uow.impl import get_uow


class ProductDependencies:
    @classmethod
    async def get_products(cls):
        return GetProducts(get_uow())
