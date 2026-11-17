from models import Order
from sqlalchemy.orm import Session


class OrderService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, order_id: str):
        order = self.session.get(Order, order_id)
        return order
