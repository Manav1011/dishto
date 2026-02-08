from django.shortcuts import render
from fastapi import APIRouter, Depends, status, HTTPException, Request
from core.schema import BaseResponse

from core.dependencies import is_outlet_admin
from .request import (
    IngredientCreationRequest, IngredientUpdateRequest, IngredientActiveRequest,
    MenuItemIngredientCreateRequest, MenuItemIngredientUpdateRequest, MenuItemIngredientDeleteRequest,
    InventoryTransactionCreateRequest, InventoryTransactionUpdateRequest
)
from .response import MenuItemIngredientObject, MenuItemIngredientObjects, InventoryTransactionObject, InventoryTransactionObjects
from .service import InventoryService
from dishto.GlobalUtils import generate_unique_hash
from decimal import Decimal
from django.db import transaction

# router
inventory_router = APIRouter(tags=["Inventory"])

# Ingredient Endpoints

@inventory_router.post(
    "/{outlet_slug}/ingredients",
    summary="Create Ingredient",
    description="""
    Create a new ingredient for the inventory.
    Requires the user to be the admin of the outlet.
    """,
)
async def create_ingredient(
    data: IngredientCreationRequest,
    service: InventoryService = Depends(InventoryService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse:
    return BaseResponse(data=await service.create_ingredient(body=data, outlet=outlet))


@inventory_router.get(
    "/{outlet_slug}/ingredients",
    summary="Get Ingredients",
    description="""
    Retrieve ingredients for an outlet.
    - If `slug` is "__all__", returns all ingredients for the outlet.
    - Otherwise, returns the ingredient matching the given slug.
    Requires the user to be the admin of the outlet.
    """,
)
async def get_ingredients(    
    slug: str,
    service: InventoryService = Depends(InventoryService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse:
    return BaseResponse(data=await service.get_ingredients(slug=slug, outlet=outlet))


@inventory_router.put(
    "/{outlet_slug}/ingredients/{slug}",
    summary="Update Ingredient",
    description="""
    Update an ingredient's fields. Only fields provided in the body will be updated.
    Requires the user to be the admin of the outlet.
    """,
)
async def update_ingredient(
    slug: str,
    data: IngredientUpdateRequest,
    service: InventoryService = Depends(InventoryService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse:
    return BaseResponse(data=await service.update_ingredient(slug=slug, body=data, outlet=outlet))


@inventory_router.delete(
    "/{outlet_slug}/ingredients/{slug}",
    summary="Delete Ingredient",
    description="""
    Delete an ingredient by slug.
    Requires the user to be the admin of the outlet.
    """,
)
async def delete_ingredient(
    slug: str,
    service: InventoryService = Depends(InventoryService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse:
    return BaseResponse(data=await service.delete_ingredient(slug=slug, outlet=outlet))


@inventory_router.patch(
    "/{outlet_slug}/ingredients/{slug}/activate",
    summary="Activate/Deactivate Ingredient",
    description="""
    Activate or deactivate an ingredient.
    Requires the user to be the admin of the outlet.
    """,
)
async def set_ingredient_active(
    slug: str,
    data: IngredientActiveRequest,
    service: InventoryService = Depends(InventoryService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse:
    return BaseResponse(data=await service.set_ingredient_active(slug=slug, is_active=data.is_active, outlet=outlet))


# Menu Item Ingredient Endpoints

@inventory_router.get(
    "/{outlet_slug}/menu_item/{menu_item_slug}/ingredients",
    summary="List MenuItem Ingredients",
    description="""
    Get all ingredients for a menu item.
    Requires the user to be the admin of the outlet.
    """,
)
async def list_menu_item_ingredients(
    menu_item_slug: str,
    service: InventoryService = Depends(InventoryService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse:
    return BaseResponse(data=await service.list_menu_item_ingredients(menu_item_slug=menu_item_slug, outlet=outlet))

@inventory_router.post(
    "/{outlet_slug}/menu_item/ingredient",
    summary="Add Ingredient to MenuItem",
    description="""
    Link an ingredient and quantity to a menu item.
    Requires the user to be the admin of the outlet.
    """,
)
async def add_menu_item_ingredient(
    data: MenuItemIngredientCreateRequest,
    service: InventoryService = Depends(InventoryService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse:
    return BaseResponse(data=await service.add_menu_item_ingredient(body=data, outlet=outlet))

@inventory_router.put(
    "/{outlet_slug}/menu_item/ingredient/{slug}",
    summary="Update MenuItemIngredient",
    description="""
    Edit ingredient mapping for a menu item.
    Requires the user to be the admin of the outlet.
    """,
)
async def update_menu_item_ingredient(
    slug: str,
    data: MenuItemIngredientUpdateRequest,
    service: InventoryService = Depends(InventoryService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse:
    return BaseResponse(data=await service.update_menu_item_ingredient(slug=slug, body=data, outlet=outlet))

@inventory_router.delete(
    "/{outlet_slug}/menu_item/ingredient/{slug}",
    summary="Delete MenuItemIngredient",
    description="""
    Remove ingredient mapping for a menu item.
    Requires the user to be the admin of the outlet.
    """,
)
async def delete_menu_item_ingredient(
    slug: str,
    service: InventoryService = Depends(InventoryService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse:
    return BaseResponse(data=await service.delete_menu_item_ingredient(slug=slug, outlet=outlet))


# Transaction Endpoints

@inventory_router.get(
    "/{outlet_slug}/transactions",
    summary="List Inventory Transactions for Outlet",
    description="""
    List all inventory transactions for an outlet.
    Requires the user to be the admin of the outlet.
    """,
)
async def list_transactions_for_outlet(
    service: InventoryService = Depends(InventoryService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse:
    return BaseResponse(data=await service.list_transactions_for_outlet(outlet=outlet))

@inventory_router.get(
    "/{outlet_slug}/ingredient/{ingredient_slug}/transactions",
    summary="List Inventory Transactions for Ingredient",
    description="""
    List all inventory transactions for an ingredient.
    Requires the user to be the admin of the outlet.
    """,
)
async def list_transactions_for_ingredient(
    ingredient_slug: str,
    service: InventoryService = Depends(InventoryService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse:
    return BaseResponse(data=await service.list_transactions_for_ingredient(ingredient_slug=ingredient_slug, outlet=outlet))

@inventory_router.post(
    "/{outlet_slug}/transactions",
    summary="Create Inventory Transaction",
    description="""
    Add a new inventory transaction (purchase, usage, wastage, adjustment).
    Requires the user to be the admin of the outlet.
    """,
)
async def create_transaction(
    data: InventoryTransactionCreateRequest,
    service: InventoryService = Depends(InventoryService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse:
    return BaseResponse(data=await service.create_transaction(body=data, outlet=outlet))

@inventory_router.get(
    "/{outlet_slug}/transactions/{slug}",
    summary="Get Inventory Transaction Details",
    description="""
    Retrieve details for a specific inventory transaction.
    Requires the user to be the admin of the outlet.
    """,
)
async def get_transaction_details(
    slug: str,
    service: InventoryService = Depends(InventoryService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse:
    return BaseResponse(data=await service.get_transaction_details(slug=slug, outlet=outlet))

@inventory_router.put(
    "/{outlet_slug}/transactions/{slug}",
    summary="Update Inventory Transaction",
    description="""
    Update an inventory transaction. Only fields provided in the body will be updated.
    Requires the user to be the admin of the outlet.
    """,
)
async def update_transaction(
    slug: str,
    data: InventoryTransactionUpdateRequest,
    service: InventoryService = Depends(InventoryService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse:
    return BaseResponse(data=await service.update_transaction(slug=slug, body=data, outlet=outlet))

@inventory_router.delete(
    "/{outlet_slug}/transactions/{slug}",
    summary="Delete Inventory Transaction",
    description="""
    Delete an inventory transaction by slug.
    Requires the user to be the admin of the outlet.
    """,
)
async def delete_transaction(
    slug: str,
    service: InventoryService = Depends(InventoryService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse:
    return BaseResponse(data=await service.delete_transaction(slug=slug, outlet=outlet))

