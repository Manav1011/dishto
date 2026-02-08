from pydantic import BaseModel, Field
from typing import Annotated, List, Optional

class OrderItemCreateRequest(BaseModel):
    item_slug: Annotated[str, Field(min_length=1)]
    quantity: int

class OrderCreateRequest(BaseModel):    
    special_instructions: Optional[str] = None
    items: List[OrderItemCreateRequest]
