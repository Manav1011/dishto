from pydantic import BaseModel, Field, condecimal, constr
from typing import Annotated, List, Optional

class IngredientCreationRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    unit: Annotated[str, Field(max_length=10)]
    current_stock: Annotated[float, Field(gt=0)]
    minimum_stock: Annotated[float, Field(gt=0)]

class IngredientUpdateRequest(BaseModel):
    name: Optional[str] = None
    unit: Optional[str] = None
    current_stock: Optional[float] = None
    minimum_stock: Optional[float] = None
    # is_active is handled by a separate API

class IngredientActiveRequest(BaseModel):
    is_active: bool

class MenuItemIngredientCreateRequest(BaseModel):
    menu_item_slug: str
    ingredient_slug: str
    quantity: float

class MenuItemIngredientUpdateRequest(BaseModel):
    quantity: Optional[float] = None

class MenuItemIngredientDeleteRequest(BaseModel):
    menu_item_slug: str
    ingredient_slug: str

class InventoryTransactionCreateRequest(BaseModel):
    ingredient_slug: str
    transaction_type: str
    quantity: float
    note: Optional[str] = None

class InventoryTransactionUpdateRequest(BaseModel):
    transaction_type: Optional[str] = None
    quantity: Optional[float] = None
    note: Optional[str] = None
