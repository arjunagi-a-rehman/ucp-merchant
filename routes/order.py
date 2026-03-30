from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.order import Order
from services.order import order_service
from security import get_current_user

router = APIRouter(
    prefix="/orders",
    tags=["order"],
    dependencies=[Depends(get_current_user)]
)

@router.get("", response_model=List[Order], summary="List Orders")
def list_orders(user_id: str = Depends(get_current_user)):
    """List all orders for the authenticated user."""
    return order_service.list_orders(user_id=user_id)

@router.get("/{order_id}", response_model=Order, summary="Get Order")
def get_order(order_id: str):
    """Retrieve an order by ID (UCP Order Capability)."""
    try:
        return order_service.get_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
