from pydantic import BaseModel
from typing import Annotated, Optional
from pydantic import Field

class FranchiseCreationRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]

from fastapi import UploadFile

class OutletCreationRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    cover_image: Optional[str] = None
    mid_page_slider: Optional[list[str]] = None  # For docs only; actual files handled in view

class MenuCategoryCreationRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]    
    description: str

class MenuCategoryUpdateRequest(BaseModel):
    name: Optional[Annotated[str, Field(min_length=1, max_length=100)]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class MenuItemCreationRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    category_slug: Annotated[str, Field(min_length=1, max_length=100)]
    description: str
    price: Annotated[float, Field(gt=0, description="Price must be greater than 0")]
    is_available: bool = True

class MenuItemUpdateRequest(BaseModel):
    name: Optional[Annotated[str, Field(min_length=1, max_length=100)]] = None
    description: Optional[str] = None
    price: Optional[Annotated[float, Field(gt=0, description="Price must be greater than 0")]] = None
    is_available: Optional[bool] = None
    
class CategoryDisplayOrderObject(BaseModel):
    category_slug: str
    display_order: int
    
class CategoryRearrangementRequest(BaseModel):    
    ordering: list[CategoryDisplayOrderObject]
    
class ItemDisplayOrderObject(BaseModel):
    menu_item_slug: str
    display_order: int
    
class ItemRearrangementRequest(BaseModel):    
    ordering: list[ItemDisplayOrderObject]