from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
from models.order import Order
from services.order import order_service
from security import get_current_user

router = APIRouter(
    prefix="/orders",
    tags=["order"],
    dependencies=[Depends(get_current_user)]
)


def _add_order_actions(order_data: dict, request: Request) -> dict:
    """Add next_actions to order responses."""
    base = str(request.base_url).rstrip("/")
    status = order_data.get("status", "")

    if status == "processing":
        order_data["next_actions"] = [{
            "action": "check_again_later",
            "description": "Order is being processed. Check back for status updates.",
            "method": "GET",
            "endpoint": f"{base}/orders/{order_data.get('id', '')}"
        }]
    elif status == "shipped":
        order_data["next_actions"] = [{
            "action": "track_shipment",
            "description": "Order has been shipped. Track delivery.",
            "tracking_url": order_data.get("tracking_url")
        }]
    elif status == "delivered":
        order_data["next_actions"] = [{
            "action": "browse_more",
            "description": "Order delivered! Browse more products.",
            "method": "GET",
            "endpoint": f"{base}/products"
        }]

    return order_data


@router.get("", summary="List Orders")
def list_orders(request: Request, user_id: str = Depends(get_current_user)):
    """List all orders for the authenticated user."""
    orders = order_service.list_orders(user_id=user_id)
    return [_add_order_actions(o.model_dump(), request) for o in orders]


@router.get("/{order_id}", summary="Get Order")
def get_order(order_id: str, request: Request):
    """
    Retrieve an order by ID.

    Example response includes next_actions telling the agent what to do based on order status.
    """
    try:
        order = order_service.get_order(order_id)
        return _add_order_actions(order.model_dump(), request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail={
            "error": str(e),
            "action": "List all orders at GET /orders to find valid order IDs"
        })
