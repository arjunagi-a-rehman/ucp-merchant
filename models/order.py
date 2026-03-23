from pydantic import BaseModel
from typing import List, Optional
from models.checkout import LineItem, Buyer

class Order(BaseModel):
    id: str
    status: str
    line_items: List[LineItem]
    buyer: Buyer
    tracking_url: Optional[str] = None
