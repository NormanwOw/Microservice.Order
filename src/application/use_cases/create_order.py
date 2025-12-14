import json
from uuid import UUID

from src.config import Settings
from src.domain.aggregates import Order
from src.domain.entities import Product
from src.domain.enums import OrderStatus
from src.domain.exceptions import ProductsDoesNotExists
from src.infrastructure.messaging.interfaces import IKafkaProducer
from src.infrastructure.messaging.messages import OrderMessage
from src.infrastructure.models import (
    OrderItemModel,
    OrderModel,
    OutboxModel,
    ProductModel,
)
from src.infrastructure.uow.interfaces import IUnitOfWork
from src.presentation.schemas import CreateOrderResponse


class CreateOrder:
    def __init__(self, uow: IUnitOfWork, producer: IKafkaProducer, settings: Settings):
        self.uow = uow
        self.producer = producer
        self.settings = settings

    async def __call__(self, order: Order) -> CreateOrderResponse:
        async with self.uow:
            id_product_mapper = {product.id: product for product in order.products}
            db_products = await self.uow.products.find_exists_by_ids(
                list(id_product_mapper.keys())
            )
            if not db_products:
                raise ProductsDoesNotExists
            products = [product.to_domain() for product in db_products]
            updated_db_products = await order.reserve_products(products)
            await self.update_products_stocks(db_products, updated_db_products)
            await self.save_order(order)
            message = await self.create_message(order)
            await self.save_message_to_outbox(message)
            await self.uow.commit()

            return CreateOrderResponse(order_id=order.order_id)

    async def update_products_stocks(
        self, db_products: list[ProductModel], updated_db_products: dict[UUID, Product]
    ):
        for product in db_products:
            if updated_db_products.get(product.id):
                product.stocks = updated_db_products[product.id].quantity

    async def save_order(self, order: Order):
        new_order = OrderModel.from_domain(order, status=OrderStatus.ORDER_CREATED)
        await self.uow.orders.add(new_order)
        for product in order.products:
            await self.uow.order_items.add(OrderItemModel.from_domain(product, order))

    async def create_message(self, order: Order) -> dict:
        return json.loads(
            OrderMessage(
                order_id=order.order_id,
                event_type=OrderStatus.ORDER_CREATED,
                aggregate_type='Order',
                payload=order.products,
            ).model_dump_json()
        )

    async def save_message_to_outbox(self, message: dict):
        for_outbox = OutboxModel(
            topic=self.settings.ORDER_EVENTS_TOPIC, message=message
        )
        await self.uow.outbox.add(for_outbox)
