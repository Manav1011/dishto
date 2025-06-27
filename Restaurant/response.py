from pydantic import BaseModel
from typing import Optional

class FranchiseObject(BaseModel):
    name: str
    slug: str

class FranchiseObjects(BaseModel):
    franchises: list[FranchiseObject]
    
class FranchiseCreationResponse(BaseModel):
    name: str
    slug: str
    
class OutletCreationResponse(BaseModel):
    name: str
    slug: str
    
class OutletObject(BaseModel):
    name: str
    slug: str
    
class OutletObjects(BaseModel):
    outlets: list[OutletObject]

class MenuCategoryCreationResponse(BaseModel):
    name: str
    description: str
    is_active: bool
    slug: str

class MenuCategoryObject(BaseModel):
    name: str
    description: str
    is_active: bool
    slug: str

class MenuCategoryObjects(BaseModel):
    categories: list[MenuCategoryObject]

class MenuCategoryUpdateResponse(BaseModel):
    name: str
    description: str
    is_active: bool
    slug: str

class MenuItemCreationResponse(BaseModel):
    name: str
    description: str
    price: float
    is_available: bool
    image: Optional[str] = None
    slug: str
    category_slug: str

class MenuItemObject(BaseModel):
    name: str
    description: str
    price: float
    is_available: bool
    image: Optional[str] = None
    slug: str
    category_slug: str

class MenuItemObjects(BaseModel):
    items: list[MenuItemObject]

class MenuItemUpdateResponse(BaseModel):
    name: str
    description: str
    price: float
    is_available: bool
    image: Optional[str] = None
    slug: str
    category_slug: str