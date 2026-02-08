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
from typing import Optional
import uuid

from core.request import OutletCreationRequest, FranchiseCreationRequest
from core.response import (
    OutletObject,
    OutletObjects,
    FranchiseObject,
    FranchiseObjects,
    OutletCreationResponse    
)

from core.response import OutletObjectsUser
from core.schema import BaseResponse
from core.service import RestaurantService
from django.core.files.base import ContentFile
from core.dependencies import is_superadmin
from core.dependencies import franchise_exists, is_franchise_admin
from core.utils.limiters import limiter


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