from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    status,
    Request,
    Query,
    Path,
)
from typing import Optional, List
import uuid

from core.request import OutletCreationRequest, FranchiseCreationRequest, OutletFeatureRequestCreateRequest, OutletFeatureRequestUpdateRequest
from core.response import (
    OutletObject,
    OutletObjects,
    FranchiseObject,
    FranchiseObjects,
    OutletCreationResponse,    
    OutletObjectsUser,
    FeatureResponse, # New
    OutletFeatureRequestResponse, # New
    OutletActiveFeatureResponse # New
)

from core.schema import BaseResponse
from core.service import RestaurantService, FeatureService # New FeatureService
from django.core.files.base import ContentFile
from core.dependencies import is_superadmin, is_outlet_admin, franchise_exists, is_franchise_admin, has_feature # New dependencies
from core.utils.limiters import limiter
from django.contrib.auth import get_user_model # New import
from .models import Outlet # New import for Outlet model

User = get_user_model() # New


# Create your views here.

end_user_router = APIRouter(tags=["End User"])

@end_user_router.get(
    path="/",
    summary="Get All Outlets",
    description="""Retrieve all outlets for the franchise.""",    
    dependencies=[Depends(franchise_exists)]
)
@limiter.limit("50/minute")
async def get_outlets_for_user(
    request: Request, service: RestaurantService = Depends(RestaurantService)
) -> BaseResponse[OutletObjectsUser]:    
    return BaseResponse(
        data=await service.get_user_outlets(franchise=request.state.franchise)
    )

restaurant_router = APIRouter(prefix="/restaurant", tags=["Restaurant"])

@restaurant_router.post(
    "/franchise/",
    summary="Create Franchise",
    description="""
    Create a new franchise.
    """,
    dependencies=[Depends(is_superadmin)],
)
async def create_franchise(
    data: FranchiseCreationRequest = Depends(),
    service: RestaurantService = Depends(RestaurantService),
):
    return BaseResponse(data=await service.create_franchise(body=data))


@restaurant_router.get(
    "/franchise",
    summary="Get Franchise",
    description="""
    Retrieve a franchise or all franchises by slug.

    - If `slug` is "__all__", returns all franchises.
    - Otherwise, returns the franchise matching the given slug.
    """,
    dependencies=[Depends(is_superadmin)],
)
async def get_franchise(
    request: Request,
    slug: str = Query(..., description="Slug of the franchise "),
    service: RestaurantService = Depends(RestaurantService),
    limit: Optional[int] = Query(None, description="Maximum number of items to return"),
    last_seen_id: Optional[int] = Query(
        None, description="The last seen item ID for pagination"
    ),
) -> BaseResponse[FranchiseObject | FranchiseObjects]:
    return BaseResponse(
        data=await service.get_franchise(
            slug=slug, limit=limit, last_seen_id=last_seen_id
        )
    )

@restaurant_router.post(
    "/outlet",
    summary="Create Outlet",
    description="""
    Create a new outlet for a given franchise.

    Requires the user to be the admin of the franchise.
    Accepts multipart/form-data with optional cover image and multiple mid page slider images.
    """,
)
async def create_outlet(
    name: str = Form(..., description="Name of the outlet"),
    cover_image: UploadFile = File(None, description="Cover image for the outlet (optional)"),
    mid_page_slider: list[UploadFile] = File(None, description="Mid page slider images (optional, multiple)"),
    service: RestaurantService = Depends(RestaurantService),
    franchise=Depends(is_franchise_admin),
) -> BaseResponse[OutletCreationResponse]:
    cover_image_file = None
    slider_image_files = []
    if cover_image is not None and cover_image.filename:
        if not cover_image.content_type or not cover_image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cover image must be an image file"
            )
        if cover_image.size and cover_image.size > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cover image file too large. Maximum size is 5MB.",
            )
        cover_image_file = ContentFile(await cover_image.read(), name=cover_image.filename)
    if mid_page_slider:
        for idx, slider_image in enumerate(mid_page_slider):
            if slider_image is not None and slider_image.filename:
                if not slider_image.content_type or not slider_image.content_type.startswith("image/"):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail=f"Slider image {idx+1} must be an image file"
                    )
                if slider_image.size and slider_image.size > 5 * 1024 * 1024:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Slider image {idx+1} file too large. Maximum size is 5MB.",
                    )
                slider_image_files.append(ContentFile(await slider_image.read(), name=slider_image.filename))

    request_data = OutletCreationRequest(name=name)
    return BaseResponse(
        data=await service.create_outlet(
            body=request_data,
            franchise=franchise,
            cover_image=cover_image_file,
            mid_page_slider=slider_image_files,
        )
    )


@restaurant_router.get(
    "/outlet",
    summary="Get Outlet",
    description="""
    Retrieve an outlet or all outlets for a franchise.

    - If `slug` is "__all__", returns all outlets for the franchise.
    - Otherwise, returns the outlet matching the given slug.

    Requires the user to be the admin of the franchise.
    """,
)
async def get_outlet(
    slug: str = Query(..., description="Slug of the outlet "),
    service: RestaurantService = Depends(RestaurantService),
    franchise=Depends(is_franchise_admin),
    limit: Optional[int] = Query(None, description="Maximum number of items to return"),
    last_seen_id: Optional[int] = Query(
        None, description="The last seen item ID for pagination"
    ),
) -> BaseResponse[OutletObject | OutletObjects]:
    return BaseResponse(
        data=await service.get_outlet(
            slug=slug,
            franchise=franchise,
            limit=limit,
            last_seen_id=last_seen_id,
        )
    )


# --- Feature Management Router ---
feature_router = APIRouter(prefix="/feature", tags=["Feature Management"])

@feature_router.get(
    "/available",
    summary="List available master features",
    description="Retrieve a list of master features that can be requested by an outlet.",
    response_model=BaseResponse[List[FeatureResponse]]
)
async def list_available_master_features(
    service: FeatureService = Depends(FeatureService)
):
    return BaseResponse(data=await service.list_available_master_features())


@feature_router.post(
    "/outlet/{outlet_slug}/requests/",
    summary="Create a new feature request for an outlet",
    description="Outlet admin submits a request to add or remove features.",
    dependencies=[Depends(is_outlet_admin)],
    response_model=BaseResponse[OutletFeatureRequestResponse]
)
async def create_feature_request(
    request: Request,
    request_data: OutletFeatureRequestCreateRequest,
    outlet: Outlet = Depends(is_outlet_admin), # is_outlet_admin returns the Outlet object
    service: FeatureService = Depends(FeatureService)
):
    requested_by_user = request.state.user
    return BaseResponse(data=await service.create_feature_request(
        outlet=outlet,
        request_data=request_data,
        requested_by_user=requested_by_user
    ))


@feature_router.get(
    "/outlet/{outlet_slug}/requests/",
    summary="List feature requests for an outlet",
    description="Retrieve all feature requests (pending, approved, rejected) for a specific outlet.",
    dependencies=[Depends(is_outlet_admin)],
    response_model=BaseResponse[List[OutletFeatureRequestResponse]]
)
async def list_outlet_feature_requests(
    outlet: Outlet = Depends(is_outlet_admin),
    service: FeatureService = Depends(FeatureService)
):
    return BaseResponse(data=await service.list_outlet_feature_requests(outlet=outlet))

@feature_router.get(
    "/outlet/{outlet_slug}/active-features",
    summary="List active features for an outlet",
    description="Retrieve a list of features currently enabled for a specific outlet, including their custom prices.",
    dependencies=[Depends(is_outlet_admin)],
    response_model=BaseResponse[List[OutletActiveFeatureResponse]]
)
async def list_outlet_active_features(
    outlet: Outlet = Depends(is_outlet_admin),
    service: FeatureService = Depends(FeatureService)
):
    return BaseResponse(data=await service.list_outlet_active_features(outlet=outlet))

@feature_router.get(
    "/admin/requests/",
    summary="List all feature requests (Superadmin)",
    description="Retrieve all feature requests from all outlets. Filterable by status.",
    dependencies=[Depends(is_superadmin)],
    response_model=BaseResponse[List[OutletFeatureRequestResponse]]
)
async def list_all_feature_requests(
    status_filter: Optional[str] = Query(None, description="Filter requests by status (pending, approved, rejected)"),
    service: FeatureService = Depends(FeatureService)
):
    return BaseResponse(data=await service.list_all_feature_requests(status_filter=status_filter))


@feature_router.patch(
    "/admin/requests/{request_id}/",
    summary="Update a feature request (Superadmin)",
    description="Approve or reject a feature request and optionally set prices for requested features.",
    dependencies=[Depends(is_superadmin)],
    response_model=BaseResponse[OutletFeatureRequestResponse]
)
async def update_feature_request(
    request_id: int,
    update_data: OutletFeatureRequestUpdateRequest,
    request: Request,
    service: FeatureService = Depends(FeatureService)
):
    approved_by_user = request.state.user
    return BaseResponse(data=await service.update_feature_request(
        request_id=request_id,
        update_data=update_data,
        approved_by_user=approved_by_user
    ))