import uuid
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.entities import Product
from src.domain.exceptions import ProductsDoesNotExists


class Order(BaseModel):
    order_id: UUID = Field(default_factory=uuid.uuid4)
    customer_id: UUID
    products: list[Product]
    created_at: datetime = Field(default_factory=datetime.now)

    async def reserve_products(self, db_products: list[Product]) -> dict[UUID, Product]:
        id_product_mapper = {product.id: product for product in self.products}
        if not db_products:
            raise ProductsDoesNotExists

        products = []
        for product in db_products:
            if not product.quantity:
                continue

            order_product: Product = id_product_mapper[product.id]
            db_product: Product = product

            order_product.name = db_product.name
            order_product.price = db_product.price
            order_product.currency = db_product.currency
            if order_product.quantity > db_product.quantity:
                order_product.quantity = db_product.quantity
                db_product.quantity = 0
            else:
                db_product.quantity -= order_product.quantity

            products.append(order_product)

        self.products = products

        return {product.id: product for product in db_products}
