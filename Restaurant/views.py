from fastapi import APIRouter, Depends

from Restaurant.response import OutletCreationResponse
from core.schema import BaseResponse

from .request import FranchiseCreationRequest, OutletCreationRequest
from .response import FranchiseObject, FranchiseObjects, OutletObject, OutletObjects
from .service import RestaurantService
from core.dependencies import is_superadmin
from .dependencies import is_franchise_admin

# Create your views here.
router = APIRouter(prefix="/restaurant", tags=["restaurant"])

@router.get("/", summary="Restaurant Root", description="Root endpoint for the restaurant service.")
async def restaurant_root():
    """
    Root endpoint for the restaurant service.
    """
    return {"message": "Welcome to the Restaurant Service!"}


@router.post("/franchise/", summary="Create Franchise", description="Create a new franchise for the restaurant service.", dependencies=[Depends(is_superadmin)])
async def create_franchise(data: FranchiseCreationRequest = Depends(), service: RestaurantService = Depends(RestaurantService)):
    """
    Create a new franchise.
    """
    # Placeholder logic for creating a franchise
    return BaseResponse(data = await service.create_franchise(body=data.model_dump()))

@router.get("/franchise/{slug}", summary="Get Franchise", description="Retrieve a franchise by slug.", dependencies=[Depends(is_superadmin)])
async def get_franchise(slug: str, service: RestaurantService = Depends(RestaurantService)) -> BaseResponse[FranchiseObject | FranchiseObjects]:
    """Retrieve a franchise by slug."""
    return BaseResponse(data = await service.get_franchise(slug=slug))


@router.post("/outlet", summary="Create Outlet", description="Create a new outlet for the restaurant service.", dependencies=[Depends(is_franchise_admin)])
async def create_outlet(data: OutletCreationRequest, service: RestaurantService = Depends(RestaurantService), user=Depends(is_franchise_admin)) -> BaseResponse[OutletCreationResponse]:
    """
    Create a new outlet.
    """
    # Placeholder logic for creating an outlet
    return BaseResponse(data = await service.create_outlet(body=data.model_dump(), user=user))

@router.get("/outlet/{franchise_slug}/{slug}", summary="Get Outlet", description="Retrieve an outlet by slug.", dependencies=[Depends(is_franchise_admin)])
async def get_outlet(franchise_slug: str, slug: str, service: RestaurantService = Depends(RestaurantService), user=Depends(is_franchise_admin)) -> BaseResponse[OutletObject | OutletObjects]:
    """Retrieve an outlet by slug."""
    return BaseResponse(data = await service.get_outlet(franchise_slug=franchise_slug, slug=slug, user=user))