import httpx
from app.config import NotFoundError


class PaymentClient:
    def __init__(self, base_url: str, timeout_seconds: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout_seconds

    def create_payment(self, order_id: str, user_id: str, amount: int) -> dict:
        json_data = {
            "order_id": order_id,
            "user_id": user_id,
            "amount": amount,
        }
        response = httpx.post(
            f"{self.base_url}/payments", timeout=self.timeout, json=json_data
        )
        if response.status_code == 404:
            raise NotFoundError(f"Payment endpoint not found: {self.base_url}/payments")

        response.raise_for_status()
        return response.json()
