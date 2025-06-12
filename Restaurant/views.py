from django.shortcuts import render
from fastapi import APIRouter

# Create your views here.
router = APIRouter(prefix="/restaurant", tags=["restaurant"])

@router.get("/", summary="Restaurant Root", description="Root endpoint for the restaurant service.")
async def restaurant_root():
    """
    Root endpoint for the restaurant service.
    """
    return {"message": "Welcome to the Restaurant Service!"}

