from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from decimal import Decimal

# --- Original Schemas (Reconstructed) ---
class FranchiseObject(BaseModel):
    name: str
    slug: str

class FranchiseObjects(BaseModel):
    franchises: List[FranchiseObject]
    last_seen_id: Optional[int] = None

class OutletSliderImageObject(BaseModel):
    image: str
    order: int

class OutletObject(BaseModel):
    name: str
    slug: str
    cover_image: Optional[str] = None
    mid_page_slider: Optional[List[OutletSliderImageObject]] = None

class OutletObjects(BaseModel):
    last_seen_id: Optional[int] = None
    outlets: List[OutletObject]

class OutletObjectsUser(BaseModel):
    outlets: List[OutletObject]

class OutletCreationResponse(BaseModel):
    name: str
    slug: str
    cover_image: Optional[str] = None
    mid_page_slider: Optional[List[OutletSliderImageObject]] = None

# --- New Schemas for Feature Management ---
class FeatureResponse(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[Decimal] = None
    slug: str

class UserResponse(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class OutletResponse(BaseModel): # Moved to be defined before OutletFeatureRequestResponse
    name: str
    slug: str
    
class OutletFeatureRequestResponse(BaseModel):
    id: int
    outlet: OutletResponse
    features: List[FeatureResponse]
    status: str
    request_type: str
    requested_by: Optional[UserResponse] = None
    approved_by: Optional[UserResponse] = None
    created_at: datetime
    updated_at: datetime
    note: Optional[str] = None

class OutletActiveFeatureResponse(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal = Field(..., description="The custom price for this feature for the specific outlet.")
    slug: str
