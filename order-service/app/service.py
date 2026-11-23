from app.api_clients import CatalogClient, PaymentClient
from app.config import NotFoundError
from models import Order, OrderItem
from schemas import OrderCreateSchema, OrderReadSchema
from sqlalchemy.orm import Session


class OrderService:
    def __init__(
        self,
        session: Session,
        catalog_client: CatalogClient,
        payment_client: PaymentClient,
    ) -> None:
        self.session = session
        self.catalog_client = catalog_client
        self.payment_client = payment_client

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
        total_amount = sum(p["unit_price"] * p["quantity"] for p in products)

        order = Order(
            user_id=order_data.user_id,
            status="created",
            total_amount=total_amount,
        )
        self.session.add(order)
        self.session.flush()

        order.items = [OrderItem(order_id=order.id, **product) for product in products]
        self.session.commit()

        self.payment_client.create_payment(
            order_id=order.id,
            user_id=order.user_id,
            amount=total_amount,
        )

        return OrderReadSchema.model_validate(Order)

    def get(self, order_id: str):
        order = self.session.get(Order, order_id)
        if order is None:
            raise NotFoundError()
        return order
