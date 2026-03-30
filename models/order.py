from pydantic import BaseModel, Field
from typing import List, Optional
from models.checkout import LineItem, BuyerInfo

class Order(BaseModel):
    id: str = Field(..., description="The finalized merchant order tracking ID.")
    status: str = Field(..., description="Shipping/Processing status (e.g., processing, shipped, delivered).")
    line_items: List[LineItem] = Field(..., description="Confirmed items in this order.")
    buyer: Optional[BuyerInfo] = Field(None, description="Finalized shipping and contact details for the order.")
    tracking_url: Optional[str] = Field(None, description="External URL to track shipment progress.")
    total: Optional[float] = Field(None, description="Total order amount in INR.")
