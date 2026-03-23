from fastapi import APIRouter, HTTPException, Depends
from models.checkout import CheckoutSessionRequest, CheckoutSessionUpdate, CheckoutSessionResponse
from services.checkout import service
from security import get_current_user

router = APIRouter(
    prefix="/checkout/sessions",
    tags=["checkout"],
    dependencies=[Depends(get_current_user)]
)

@router.post("", response_model=CheckoutSessionResponse, summary="Create Checkout Session")
def create_session(req: CheckoutSessionRequest):
    """
    Starts a new UCP checkout process.
    Initial state: **incomplete**.
    Returns a unique session ID to track the transaction.
    """
    return service.create_session(req)

@router.post("/{session_id}/update", response_model=CheckoutSessionResponse, summary="Update Checkout Session")
def update_session(session_id: str, update: CheckoutSessionUpdate):
    """
    Provides buyer details (shipping/payment) to the session.
    Transitions state from **incomplete** to **ready_for_complete** if all data is valid.
    """
    try:
        return service.update_session(session_id, update)
    except ValueError as e:
        status_code = 404 if "not found" in str(e) else 400
        raise HTTPException(status_code=status_code, detail=str(e))

@router.post("/{session_id}/complete", response_model=CheckoutSessionResponse, summary="Finalize Checkout")
def complete_session(session_id: str):
    """
    Finalizes the purchase. 
    State transitions to **complete**.
    This triggers the actual order creation in the merchant's backend.
    """
    try:
        return service.complete_session(session_id)
    except ValueError as e:
        status_code = 404 if "not found" in str(e) else 400
        raise HTTPException(status_code=status_code, detail=str(e))
