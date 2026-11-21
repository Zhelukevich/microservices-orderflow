from app.config import NotFoundError
from catalog_client import CatalogClient
from models import Order, OrderItem
from schemas import OrderCreateSchema, OrderReadSchema
from sqlalchemy.orm import Session


class OrderService:
    def __init__(self, session: Session, catalog_client: CatalogClient) -> None:
        self.session = session
        self.catalog_client = catalog_client

    def create(self, order_data: OrderCreateSchema) -> OrderReadSchema:
        products = []
        for item in order_data.items:
            product = self.catalog_client.get_product(item.product_id)
            products.append(
                {
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "quantity": item.quantity,
                    "unit_price": product["price"],
                }
            )
        total_amount = [product["unit_price"] for product in products]
        order = Order(
            user_id=order_data.user_id,
            status="create",
            total_amount=total_amount,
        )
        self.session.add(order)
        self.session.flush()

        order.items = [OrderItem(order_id=order.id, **product) for product in products]
        self.session.commit()

        return OrderReadSchema.model_validate(Order)

    def get(self, order_id: str):
        order = self.session.get(Order, order_id)
        if order is None:
            raise NotFoundError()
        return order
