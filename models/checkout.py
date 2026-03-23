from pydantic import BaseModel, Field
from typing import List, Optional

class LineItem(BaseModel):
    id: str = Field(..., description="Unique ID for the item (SKU or product ID).")
    name: str = Field(..., description="Human-readable name of the item.")
    quantity: int = Field(..., description="Number of items being purchased.")
    price: float = Field(..., description="Unit price of the item.")

class BuyerAddress(BaseModel):
    city: str = Field(..., description="City of the shipping address.")
    state: str = Field(..., description="State or province code (e.g., NY).")

class BuyerInfo(BaseModel):
    email: str = Field(..., description="Email address of the buyer for receipt delivery.")
    shipping_address: BuyerAddress = Field(..., description="Standard UCP shipping address object.")
    payment_method: str = Field(..., description="Payment method handle or token provided by the agent.")

class CheckoutSessionRequest(BaseModel):
    line_items: List[LineItem] = Field(..., description="List of items as defined by the merchant catalog.")

class CheckoutSessionUpdate(BaseModel):
    buyer: BuyerInfo = Field(..., description="Updates the session with mandatory buyer details for transition to 'ready_for_complete'.")

class CheckoutSessionResponse(BaseModel):
    id: str = Field(..., description="Globally unique checkout session ID (UUID).")
    status: str = Field(..., description="Current UCP checkout state (incomplete, ready_for_complete, complete).")
    line_items: List[LineItem] = Field(..., description="Current list of items in the cart.")
    buyer: Optional[BuyerInfo] = Field(None, description="Buyer information if it has been provided.")
