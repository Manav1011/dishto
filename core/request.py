from pydantic import BaseModel
from typing import Annotated, Optional
from pydantic import Field


class OutletCreationRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    cover_image: Optional[str] = None
    mid_page_slider: Optional[list[str]] = None  # For docs only; actual files handled in view
    
class FranchiseCreationRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]