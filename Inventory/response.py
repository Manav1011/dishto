from decimal import Decimal
from pydantic import BaseModel, condecimal
from typing import List, Optional

class IngredientCreationResponse(BaseModel):
    name: str
    unit: str
    current_stock: float
    minimum_stock: float
    slug: str

class IngredientObject(BaseModel):
    name: str
    unit: str
    current_stock: float
    minimum_stock: float
    is_active: bool
    slug: str

class IngredientObjects(BaseModel):
    ingredients: list[IngredientObject]

class MenuItemIngredientObject(BaseModel):
    menu_item_slug: str
    ingredient_slug: str
    quantity: float
    slug: str

class MenuItemIngredientObjects(BaseModel):
    ingredients: list[MenuItemIngredientObject]

class InventoryTransactionObject(BaseModel):
    ingredient_slug: str
    transaction_type: str
    quantity: float
    note: Optional[str] = None
    outlet_slug: str
    slug: str

class InventoryTransactionObjects(BaseModel):
    transactions: list[InventoryTransactionObject]
