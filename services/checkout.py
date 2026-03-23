import uuid
from models.checkout import CheckoutSessionResponse, CheckoutSessionRequest, CheckoutSessionUpdate

class CheckoutService:
    def __init__(self):
        self.sessions = {}
        
    def create_session(self, req: CheckoutSessionRequest) -> CheckoutSessionResponse:
        session_id = str(uuid.uuid4())
        session = CheckoutSessionResponse(
            id=session_id,
            status="incomplete",
            line_items=req.line_items,
            buyer=req.buyer
        )
        self.sessions[session_id] = session
        return session
        
    def update_session(self, session_id: str, update: CheckoutSessionUpdate) -> CheckoutSessionResponse:
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        session = self.sessions[session_id]
        if update.buyer:
            session.buyer = update.buyer
        
        # If sufficient info exists, move to ready_for_complete
        if session.buyer and session.buyer.shipping_address and session.buyer.payment_method:
            session.status = "ready_for_complete"
            
        self.sessions[session_id] = session
        return session
        
    def complete_session(self, session_id: str) -> CheckoutSessionResponse:
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        session = self.sessions[session_id]
        if session.status != "ready_for_complete":
            raise ValueError("Session is not ready for completion")
        session.status = "complete"
        self.sessions[session_id] = session
        
        # When checkout completes, generate the corresponding Order
        from services.order import order_service
        order_id = f"ORD-{session_id[:8]}"
        order_service.create_order(
            order_id=order_id,
            line_items=session.line_items,
            buyer=session.buyer
        )
        return session

service = CheckoutService()
