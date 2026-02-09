from pydantic import BaseModel, Field
from typing import Annotated, List, Optional, Literal
from datetime import datetime
from decimal import Decimal

# --- Original Schemas (Reconstructed) ---
class FranchiseCreationRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255)]

class OutletCreationRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255)]

# --- New Schemas for Feature Management ---
class FeaturePriceUpdateRequest(BaseModel):
    feature_slug: Annotated[str, Field(min_length=1)]
    price: Annotated[Decimal, Field(gt=0)]

class OutletFeatureRequestCreateRequest(BaseModel):
    feature_slugs: Annotated[List[str], Field(min_items=1)]
    request_type: Literal['add', 'remove']
    note: Optional[str] = None

class OutletFeatureRequestUpdateRequest(BaseModel):
    status: Literal['pending', 'approved', 'rejected']
    note: Optional[str] = None
    feature_prices: Optional[List[FeaturePriceUpdateRequest]] = None