from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class LineItem(BaseModel):
    id: str
    name: str
    quantity: int
    price: float

class Buyer(BaseModel):
    email: Optional[str] = None
    shipping_address: Optional[Dict[str, Any]] = None
    payment_method: Optional[str] = None

class CheckoutSessionRequest(BaseModel):
    line_items: List[LineItem]
    buyer: Optional[Buyer] = None

class CheckoutSessionUpdate(BaseModel):
    buyer: Buyer

class CheckoutSessionResponse(BaseModel):
    id: str
    status: str
    line_items: List[LineItem]
    buyer: Optional[Buyer] = None
