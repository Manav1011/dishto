from decimal import Decimal
from pydantic import BaseModel
from typing import List, Optional

class OrderItemResponse(BaseModel):
    item_slug: str
    quantity: int
    price: Decimal
    slug: str

class OrderResponse(BaseModel):
    outlet_slug: str
    order_date: str
    status: str
    total_amount: Decimal
    special_instructions: str | None
    slug: str
    items: List[OrderItemResponse]
