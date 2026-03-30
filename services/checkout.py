import httpx
from models.checkout import CheckoutSessionResponse, CheckoutSessionRequest, CheckoutSessionUpdate
from config import STOREFRONT_URL


def _map_response(data: dict) -> CheckoutSessionResponse:
    """Map storefront camelCase response to UCP snake_case model."""
    # Storefront uses lineItems, UCP uses line_items
    line_items = data.get("line_items") or data.get("lineItems") or []

    # Map buyer fields
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

    return CheckoutSessionResponse(
        id=data.get("id", ""),
        status=data.get("status", "incomplete"),
        line_items=line_items,
        buyer=buyer,
        order_id=data.get("orderId") or data.get("order_id"),
    )


class CheckoutService:
    def __init__(self):
        self.base_url = f"{STOREFRONT_URL}/api/checkout/sessions"

    def get_session(self, session_id: str) -> CheckoutSessionResponse:
        with httpx.Client(timeout=30) as client:
            resp = client.get(f"{self.base_url}/{session_id}")
            if resp.status_code == 404:
                raise ValueError("Session not found")
            resp.raise_for_status()
            return _map_response(resp.json())

    def create_session(self, req: CheckoutSessionRequest, user_id: str = "") -> CheckoutSessionResponse:
        with httpx.Client(timeout=30) as client:
            resp = client.post(self.base_url, json={
                "line_items": [item.model_dump() for item in req.line_items],
                "user_id": user_id,
            })
            resp.raise_for_status()
            return _map_response(resp.json())

    def update_session(self, session_id: str, update: CheckoutSessionUpdate) -> CheckoutSessionResponse:
        with httpx.Client(timeout=30) as client:
            # Send in both formats so storefront can handle either
            buyer = update.buyer.model_dump()
            # Also send camelCase version for storefront compatibility
            buyer_payload = {
                "email": buyer["email"],
                "shippingAddress": buyer["shipping_address"],
                "paymentMethod": buyer["payment_method"],
            }
            resp = client.post(
                f"{self.base_url}/{session_id}/update",
                json={"buyer": buyer_payload},
            )
            if resp.status_code == 404:
                raise ValueError("Session not found")
            if resp.status_code == 400:
                raise ValueError(resp.json().get("error", "Bad request"))
            resp.raise_for_status()
            return _map_response(resp.json())

    def complete_session(self, session_id: str) -> CheckoutSessionResponse:
        with httpx.Client(timeout=30) as client:
            resp = client.post(f"{self.base_url}/{session_id}/complete")
            if resp.status_code == 404:
                raise ValueError("Session not found")
            if resp.status_code == 400:
                raise ValueError(resp.json().get("error", "Bad request"))
            resp.raise_for_status()
            return _map_response(resp.json())


service = CheckoutService()
