from pydantic import BaseModel
from typing import Optional

class OutletSliderImageObject(BaseModel):
    image: str
    order: int


class OutletObject(BaseModel):
    name: str
    slug: str
    cover_image: str | None = None
    mid_page_slider: list[OutletSliderImageObject] | None = None

class OutletObjectsUser(BaseModel):
    outlets: list[OutletObject]
    
class FranchiseObject(BaseModel):
    name: str
    slug: str

class FranchiseObjects(BaseModel):
    franchises: list[FranchiseObject]
    last_seen_id: Optional[int] = None
    
class FranchiseCreationResponse(BaseModel):
    name: str
    slug: str
    
class OutletSliderImageObject(BaseModel):
    image: str
    order: int

class OutletCreationResponse(BaseModel):
    name: str
    slug: str
    cover_image: Optional[str] = None
    mid_page_slider: Optional[list[OutletSliderImageObject]] = None
    
class OutletObject(BaseModel):
    name: str
    slug: str
    cover_image: Optional[str] = None
    mid_page_slider: Optional[list[OutletSliderImageObject]] = None
    
class OutletObjects(BaseModel):
    last_seen_id: Optional[int] = None
    outlets: list[OutletObject]