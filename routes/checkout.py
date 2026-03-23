from fastapi import APIRouter, HTTPException, Depends
from models.checkout import CheckoutSessionRequest, CheckoutSessionUpdate, CheckoutSessionResponse
from services.checkout import service
from security import get_current_user

router = APIRouter(
    prefix="/checkout/sessions",
    tags=["checkout"],
    dependencies=[Depends(get_current_user)]
)

@router.post("", response_model=CheckoutSessionResponse)
def create_session(req: CheckoutSessionRequest):
    return service.create_session(req)

@router.post("/{session_id}/update", response_model=CheckoutSessionResponse)
def update_session(session_id: str, update: CheckoutSessionUpdate):
    try:
        return service.update_session(session_id, update)
    except ValueError as e:
        status_code = 404 if "not found" in str(e) else 400
        raise HTTPException(status_code=status_code, detail=str(e))

@router.post("/{session_id}/complete", response_model=CheckoutSessionResponse)
def complete_session(session_id: str):
    try:
        return service.complete_session(session_id)
    except ValueError as e:
        status_code = 404 if "not found" in str(e) else 400
        raise HTTPException(status_code=status_code, detail=str(e))
