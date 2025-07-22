from django.shortcuts import render
from fastapi import APIRouter
from Restaurant.dependencies import is_outlet_admin
# router
inventory_router = APIRouter(tags=["Inventory"])


# Views
inventory_router.post(
    path="/{outlet_slug}/ingredients",
    summary="Create Ingredient",
    description="Create a new ingredient for the inventory."
)
async def create_ingredient(
    
):
    """
    Create a new ingredient for the inventory.
    Requires outlet admin permissions.
    """
    # Logic to create ingredient
    pass