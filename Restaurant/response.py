from pydantic import BaseModel
from typing import Optional

class FranchiseObject(BaseModel):
    name: str
    slug: str

class FranchiseObjects(BaseModel):
    franchises: list[FranchiseObject]
    last_seen_id: Optional[int] = None
    
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
    last_seen_id: Optional[int] = None
    outlets: list[OutletObject]

class MenuCategoryCreationResponse(BaseModel):
    name: str
    description: str
    is_active: bool
    slug: str
    image: Optional[str] = None

class MenuCategoryObject(BaseModel):
    name: str
    description: str
    is_active: bool
    image: Optional[str] = None
    slug: str

class MenuCategoryObjects(BaseModel):
    last_seen_order: Optional[int] = None
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
    category_slug: Optional[str] = None

class MenuItemObjects(BaseModel):
    last_seen_order: Optional[int] = None
    items: list[MenuItemObject]

class MenuItemUpdateResponse(BaseModel):
    name: str
    description: str
    price: float
    is_available: bool
    image: Optional[str] = None
    slug: str
    category_slug: str
    
class OutletObjectsUser(BaseModel):
    outlets: list[OutletObject]
    
class MenuItemObjectsUser(BaseModel):
    items: list[MenuItemObject]
    
class MenuItemsContextualSearchResponse(BaseModel):
    items: list[str]