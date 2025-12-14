from src.domain.entities import Product
from src.infrastructure.uow.interfaces import IUnitOfWork


class GetProducts:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def __call__(self) -> list[Product]:
        async with self.uow:
            return [
                product.to_domain() for product in await self.uow.products.find_all()
            ]
