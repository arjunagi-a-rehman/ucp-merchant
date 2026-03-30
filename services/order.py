import httpx
from models.order import Order
from config import STOREFRONT_URL


def _map_order(data: dict) -> Order:
    """Map storefront camelCase response to UCP snake_case model."""
    line_items = data.get("line_items") or data.get("lineItems") or []

    buyer = data.get("buyer")
    if buyer and isinstance(buyer, dict):
        addr = buyer.get("shipping_address") or buyer.get("shippingAddress")
        if addr:
            buyer = {
                "email": buyer.get("email", ""),
                "shipping_address": {
                    "street": addr.get("street", ""),
                    "city": addr.get("city", ""),
                    "state": addr.get("state", ""),
                    "zip": addr.get("zip", ""),
                },
                "payment_method": buyer.get("payment_method") or buyer.get("paymentMethod", "razorpay"),
            }

    return Order(
        id=data.get("id", ""),
        status=data.get("status", "unknown"),
        line_items=line_items,
        buyer=buyer,
        tracking_url=data.get("tracking_url") or data.get("trackingUrl"),
        total=data.get("total"),
    )


class OrderService:
    def __init__(self):
        self.base_url = f"{STOREFRONT_URL}/api/orders"

    def get_order(self, order_id: str) -> Order:
        with httpx.Client(timeout=30) as client:
            resp = client.get(f"{self.base_url}/{order_id}")
            if resp.status_code == 404:
                raise ValueError("Order not found")
            resp.raise_for_status()
            return _map_order(resp.json())

    def list_orders(self, user_id: str = None) -> list[Order]:
        with httpx.Client(timeout=30) as client:
            params = {}
            if user_id:
                params["user_id"] = user_id
            resp = client.get(self.base_url, params=params)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list):
                return [_map_order(o) for o in data]
            return []


order_service = OrderService()
