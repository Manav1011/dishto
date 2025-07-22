from pydantic import BaseModel
from typing import Annotated, Optional
from pydantic import Field

class IngredientCreationRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    unit: Annotated[str, Field(max_length=10)]
    current_stock: Annotated[float, Field(gt=0)]
    minimum_stock: Annotated[float, Field(gt=0)]