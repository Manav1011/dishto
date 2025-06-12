from fastapi import APIRouter, Depends

from .request import FranchiseCreationRequest
from .service import RestaurantService
from .dependencies import is_superadmin
# Create your views here.
router = APIRouter(prefix="/restaurant", tags=["restaurant"])

@router.get("/", summary="Restaurant Root", description="Root endpoint for the restaurant service.")
async def restaurant_root():
    """
    Root endpoint for the restaurant service.
    """
    return {"message": "Welcome to the Restaurant Service!"}


@router.post("/franchise", summary="Create Franchise", description="Create a new franchise for the restaurant service.", dependencies=[Depends(is_superadmin)])
async def create_franchise(data: FranchiseCreationRequest, service: RestaurantService = Depends(RestaurantService)):
    """
    Create a new franchise.
    """
    # Placeholder logic for creating a franchise
    return await service.create_franchise(body=data.model_dump())