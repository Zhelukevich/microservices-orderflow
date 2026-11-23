import httpx
from app.config import NotFoundError


class CatalogClient:
    def __init__(self, base_url: str, timeout_seconds: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout_seconds

    def get_product(self, product_id: str) -> dict:
        response = httpx.get(
            f"{self.base_url}/products/{product_id}",
            timeout=self.timeout,
        )
        if response.status_code == 404:
            raise NotFoundError(f"Product {product_id} not found")

        response.raise_for_status()
        return response.json()
