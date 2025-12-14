from fastapi import APIRouter
from fastapi.params import Depends

from src.application.use_cases.get_products import GetProducts
from src.config import VERSION
from src.domain.entities import Product
from src.presentation.dependencies.product_dependencies import ProductDependencies

router = APIRouter(prefix=f'/api/v{VERSION}/products', tags=['Products'])


@router.get(path='', summary='Получение списка товаров')
async def get_products(
    get_prod: GetProducts = Depends(ProductDependencies.get_products),
) -> list[Product]:
    return await get_prod()
