from fastapi import APIRouter, HTTPException, Depends, Request
from models.checkout import CheckoutSessionRequest, CheckoutSessionUpdate, CheckoutSessionResponse
from services.checkout import service
from security import get_current_user

router = APIRouter(
    prefix="/checkout/sessions",
    tags=["checkout"],
    dependencies=[Depends(get_current_user)]
)


def _add_next_actions(response: CheckoutSessionResponse, request: Request) -> dict:
    """Add state machine next_actions to every checkout response."""
    base = str(request.base_url).rstrip("/")
    data = response.model_dump()
    session_id = data.get("id", "")
    status = data.get("status", "")

    if status == "incomplete":
        data["next_actions"] = [{
            "action": "update_buyer",
            "method": "POST",
            "endpoint": f"{base}/checkout/sessions/{session_id}/update",
            "description": "Add buyer email, shipping address, and payment method",
            "required_fields": ["buyer.email", "buyer.shipping_address.city", "buyer.shipping_address.state"],
            "optional_fields": ["buyer.shipping_address.street", "buyer.shipping_address.zip", "buyer.payment_method"],
            "example": {
                "buyer": {
                    "email": "user@example.com",
                    "shipping_address": {"street": "123 MG Road", "city": "Bangalore", "state": "KA", "zip": "560001"},
                    "payment_method": "razorpay"
                }
            }
        }]
    elif status == "ready_for_complete":
        total = sum(item.price * item.quantity for item in response.line_items)
        data["total"] = total
        data["next_actions"] = [{
            "action": "complete",
            "method": "POST",
            "endpoint": f"{base}/checkout/sessions/{session_id}/complete",
            "description": "Finalize the purchase. Confirm with user before calling.",
            "request_body": None
        }]
    elif status == "complete":
        data["next_actions"] = [{
            "action": "check_order",
            "method": "GET",
            "endpoint": f"{base}/orders/{data.get('order_id', '')}",
            "description": "Track the order status"
        }]

    return data


@router.post("", summary="Create Checkout Session")
def create_session(req: CheckoutSessionRequest, request: Request, user_id: str = Depends(get_current_user)):
    """
    Starts a new UCP checkout process.

    **State: incomplete** → Next: update buyer info.

    Example request:
    ```json
    {
      "line_items": [
        {"id": "abc123", "name": "Wireless Headphones", "quantity": 2, "price": 4999}
      ]
    }
    ```
    """
    result = service.create_session(req, user_id=user_id)
    return _add_next_actions(result, request)


@router.get("/{session_id}", summary="Get Checkout Session")
def get_session(session_id: str, request: Request):
    """Retrieve the current state of a checkout session with next_actions."""
    try:
        result = service.get_session(session_id)
        return _add_next_actions(result, request)
    except ValueError as e:
        detail = str(e)
        status_code = 404 if "not found" in detail else 400
        raise HTTPException(status_code=status_code, detail={
            "error": detail,
            "action": "Create a new session at POST /checkout/sessions" if status_code == 404 else detail,
        })


@router.post("/{session_id}/update", summary="Update Checkout Session")
def update_session(session_id: str, update: CheckoutSessionUpdate, request: Request):
    """
    Provides buyer details (shipping/payment) to the session.

    **Transitions: incomplete → ready_for_complete** when all required buyer fields are present.

    Example request:
    ```json
    {
      "buyer": {
        "email": "user@example.com",
        "shipping_address": {"city": "Bangalore", "state": "KA"},
        "payment_method": "razorpay"
      }
    }
    ```
    """
    try:
        result = service.update_session(session_id, update)
        return _add_next_actions(result, request)
    except ValueError as e:
        detail = str(e)
        status_code = 404 if "not found" in detail else 400
        raise HTTPException(status_code=status_code, detail={
            "error": detail,
            "action": "Ensure the session exists and is not already complete" if status_code == 400 else "Session not found. Create a new one at POST /checkout/sessions",
        })


@router.post("/{session_id}/complete", summary="Finalize Checkout")
def complete_session(session_id: str, request: Request):
    """
    Finalizes the purchase and creates the order.

    **Transitions: ready_for_complete → complete**

    Returns the order_id in the response.
    """
    try:
        result = service.complete_session(session_id)
        return _add_next_actions(result, request)
    except ValueError as e:
        detail = str(e)
        status_code = 404 if "not found" in detail else 400
        error_response = {"error": detail}
        if "not ready" in detail.lower():
            error_response["action"] = "Add buyer info first at POST /checkout/sessions/{session_id}/update"
            error_response["required_fields"] = ["buyer.email", "buyer.shipping_address"]
        raise HTTPException(status_code=status_code, detail=error_response)
