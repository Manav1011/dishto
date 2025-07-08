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

from Restaurant.response import OutletCreationResponse
from core.schema import BaseResponse

from .request import (
    FranchiseCreationRequest,
    OutletCreationRequest,
    MenuCategoryCreationRequest,
    MenuCategoryUpdateRequest,
    MenuItemCreationRequest,
    MenuItemUpdateRequest,
    CategoryRearrangementRequest,
    ItemRearrangementRequest,
)
from .response import (
    FranchiseObject,
    FranchiseObjects,
    MenuItemObjectsUser,
    MenuItemsContextualSearchResponse,
    OutletObject,
    OutletObjects,
    MenuCategoryCreationResponse,
    MenuCategoryObject,
    MenuCategoryObjects,
    MenuCategoryUpdateResponse,
    MenuItemCreationResponse,
    MenuItemObject,
    MenuItemObjects,
    MenuItemUpdateResponse,
    OutletObjectsUser,
)
from .service import RestaurantService, MenuService, UserRestaurantService
from .models import MenuCategory, MenuItem, CategoryImage
from django.core.files.base import ContentFile
from core.dependencies import is_superadmin
from .dependencies import franchise_exists, is_franchise_admin, is_outlet_admin
from .utils import generate_menu_item_image
from core.utils.limiters import limiter
from slowapi.util import get_remote_address

# User Side Router - No Authentication Required
end_user_router = APIRouter(tags=["End User"])


@end_user_router.get(
    path="/",
    summary="Get All Outlets",
    description="""Retrieve all outlets for the franchise.""",    
    dependencies=[Depends(franchise_exists)]
)
@limiter.limit("10/minute")
async def get_outlets_for_user(
    request: Request, service: UserRestaurantService = Depends(UserRestaurantService)
) -> BaseResponse[OutletObjectsUser]:
    return BaseResponse(
        data=await service.get_user_outlets(franchise=request.state.franchise)
    )


@end_user_router.get(
    "/menu/{outlet_slug}",
    summary="Get Menu for Outlet",
    description="""Retrieve the menu for a specific outlet by slug.""",
    dependencies=[Depends(franchise_exists)]
)
@limiter.limit("10/minute", key_func=get_remote_address)
async def get_menu_for_outlet(
    request: Request,
    outlet_slug: str = Path(..., description="Slug of the outlet"),
    service: UserRestaurantService = Depends(UserRestaurantService),
) -> BaseResponse[MenuItemObjectsUser]:
    return BaseResponse(
        data=await service.get_menu_for_outlet(
            franchise=request.state.franchise, outlet_slug=outlet_slug
        )
    )


@end_user_router.get(
    "/menu/{outlet_slug}/search/contextual",
    summary="Search Menu Items Contextually",
    description="""Search for menu items in a specific outlet contextually by slug.""",
    dependencies=[Depends(franchise_exists)]
)
@limiter.limit("10/minute")
async def search_menu_items_contextually(
    request: Request,
    outlet_slug: str = Path(..., description="Slug of the outlet"),
    query: str = Query(..., description="Search query"),
    service: UserRestaurantService = Depends(UserRestaurantService),
) -> BaseResponse[MenuItemsContextualSearchResponse]:
    return BaseResponse(
        data=await service.search_menu_items_contextually(
            outlet_slug=outlet_slug, query=query
        )
    )


# Admin router
router = APIRouter(prefix="/restaurant", tags=["restaurant"])


@router.post(
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


@router.get(
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


@router.post(
    "/outlet",
    summary="Create Outlet",
    description="""
    Create a new outlet for a given franchise.

    Requires the user to be the admin of the franchise.
    """,
)
async def create_outlet(
    data: OutletCreationRequest,
    service: RestaurantService = Depends(RestaurantService),
    franchise=Depends(is_franchise_admin),
) -> BaseResponse[OutletCreationResponse]:
    return BaseResponse(
        data=await service.create_outlet(body=data, franchise=franchise)
    )


@router.get(
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


@router.post(
    "/{outlet_slug}/categories",
    summary="Create Menu Category",
    description="""
    Create a new menu category for an outlet.

    Requires the user to be the admin of the outlet.
    """,
)
async def create_menu_category(
    data: MenuCategoryCreationRequest,
    service: MenuService = Depends(MenuService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse[MenuCategoryCreationResponse]:
    return BaseResponse(
        data=await service.create_menu_category(body=data, outlet=outlet)
    )


@router.get(
    "/{outlet_slug}/categories",
    summary="Get Menu Category",
    description="""
    Retrieve a menu category or all categories for an outlet.

    - If `slug` is "__all__", returns all categories for the outlet.
    - Otherwise, returns the category matching the given slug.

    Requires the user to be the admin of the outlet.
    """,
)
async def get_menu_category(
    service: MenuService = Depends(MenuService),
    outlet=Depends(is_outlet_admin),
    slug: str = Query(..., description="Slug of the category to search categories in"),
    limit: Optional[int] = Query(None, description="Maximum number of items to return"),
    last_seen_order: Optional[int] = Query(
        None, description="The last seen item ID for pagination"
    ),
) -> BaseResponse[MenuCategoryObject | MenuCategoryObjects]:
    return BaseResponse(
        data=await service.get_menu_category(
            slug=slug,
            outlet=outlet,
            limit=limit,
            last_seen_order=last_seen_order,
        )
    )


@router.get(
    "/{outlet_slug}/categories/search",
    summary="Search Menu Category",
    description="""
    Search for a menu category by slug."
    - ?query=search_term: Search term to filter categories by name or description.
    """,
)
async def search_menu_categories(
    service: MenuService = Depends(MenuService),
    outlet=Depends(is_outlet_admin),
    query: str = Query(
        None, description="Search term to filter categories by name or description"
    ),
    limit: Optional[int] = Query(10, description="Maximum number of items to return"),
) -> BaseResponse[MenuCategoryObjects]:
    return BaseResponse(
        data=await service.search_menu_categories(
            outlet=outlet, query=query, limit=limit
        )
    )


@router.put(
    "/{outlet_slug}/categories/{slug}",
    summary="Update Menu Category",
    description="""
    Update an existing menu category for an outlet.

    Requires the user to be the admin of the outlet.
    """,
)
async def update_menu_category(
    slug: str,
    data: MenuCategoryUpdateRequest,
    service: MenuService = Depends(MenuService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse[MenuCategoryUpdateResponse]:
    return BaseResponse(
        data=await service.update_menu_category(slug=slug, body=data, outlet=outlet)
    )


@router.delete(
    "/{outlet_slug}/categories/{slug}",
    summary="Delete Menu Category",
    description="""
    Delete a menu category for an outlet.

    Requires the user to be the admin of the outlet.
    """,
)
async def delete_menu_category(
    slug: str,
    service: MenuService = Depends(MenuService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse[dict]:
    return BaseResponse(
        data=await service.delete_menu_category(slug=slug, outlet=outlet)
    )


@router.post(
    "/{outlet_slug}/categories/rearrange_display_order",
    summary="Rearrange Menu Category Display Order",
    description="""
    Rearrange the display order of menu categories for an outlet.""",
)
async def rearrange_menu_category_display_order(
    data: CategoryRearrangementRequest,
    service: MenuService = Depends(MenuService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse[MenuCategoryObjects]:
    return BaseResponse(
        data=await service.rearrange_menu_category_display_order(
            body=data, outlet=outlet
        )
    )


@router.post(
    "/{outlet_slug}/items",
    summary="Create Menu Item",
    description="""
    Create a new menu item with image upload.

    Requires the user to be the admin of the outlet.

    Accepts multipart/form-data with image file.
    """,
)
async def create_menu_item(
    *,
    name: str = Form(..., description="Name of the menu item"),
    category_slug: str = Form(..., description="Slug of the menu category"),
    description: str = Form(..., description="Description of the menu item"),
    price: float = Form(..., description="Price of the menu item"),
    is_available: bool = Form(True, description="Whether the item is available"),
    image: UploadFile = File(..., description="Image file for the menu item"),
    service: MenuService = Depends(MenuService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse[MenuItemCreationResponse]:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image"
        )

    if image.size and image.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file too large. Maximum size is 5MB.",
        )

    file_content = await image.read()

    django_file = ContentFile(file_content)
    request_data = MenuItemCreationRequest(
        name=name,
        category_slug=category_slug,
        description=description,
        price=price,
        is_available=is_available,
    )
    return BaseResponse(
        data=await service.create_menu_item(body=request_data, image_file=django_file)
    )


@router.post(
    "/{outlet_slug}/items/no-image",
    summary="Create Menu Item (No Image)",
    description="""
    Create a new menu item without image upload.

    Generates a photorealistic image using Gemini based on the menu item name and description.

    Requires the user to be the admin of the outlet.
    """,
)
async def create_menu_item_no_image(
    data: MenuItemCreationRequest,
    service: MenuService = Depends(MenuService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse[MenuItemCreationResponse]:
    django_image = await generate_menu_item_image(
        food_name=data.name, description=data.description
    )
    return BaseResponse(
        data=await service.create_menu_item(body=data, image_file=django_image)
    )


@router.get(
    "/{outlet_slug}/items/enhance_description_with_ai",
    summary="Enhance Menu Item Description with AI",
    description="""
    Enhance the description of a menu item using AI.

    Requires the user to be the admin of the outlet.    
    """,
)
async def enhance_menu_item_description_with_ai(
    item_name: str = Query(..., description="Name of the menu item"),
    description: str = Query(..., description="Description of the menu item"),
    service: MenuService = Depends(MenuService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse[str]:
    enhanced_description = await service.enhance_menu_item_description_with_ai(
        item_name=item_name, description=description
    )
    return BaseResponse(data=enhanced_description)


@router.get(
    "/{outlet_slug}/items",
    summary="Get Menu Item",
    description="""
    Retrieve menu items by category slug and item slug.

    - If `slug` is "__all__", returns all items for the category.
    - Otherwise, returns the item matching the given slug.

    Requires the user to be the admin of the outlet.
    """,
)
async def get_menu_item(
    category_slug: str = Query(..., description="Slug of the menu category"),
    slug: str = Query(..., description="Slug of the menu item"),
    service: MenuService = Depends(MenuService),
    outlet=Depends(is_outlet_admin),
    limit: Optional[int] = Query(None, description="Maximum number of items to return"),
    last_seen_order: Optional[int] = Query(
        None, description="The last seen item ID for pagination"
    ),
) -> BaseResponse[MenuItemObject | MenuItemObjects]:
    return BaseResponse(
        data=await service.get_menu_item(
            category_slug=category_slug,
            slug=slug,
            outlet=outlet,
            limit=limit,
            last_seen_order=last_seen_order,
        )
    )


@router.put(
    "/{outlet_slug}/items/{category_slug}/{slug}",
    summary="Update Menu Item",
    description="""
    Update an existing menu item with optional image upload.

    Requires the user to be the admin of the outlet.

    Accepts multipart/form-data with optional image file.
    """,
)
async def update_menu_item(
    category_slug: str,
    slug: str,
    *,
    name: Optional[str] = Form(None, description="Name of the menu item"),
    description: Optional[str] = Form(None, description="Description of the menu item"),
    price: Optional[float] = Form(None, description="Price of the menu item"),
    is_available: Optional[bool] = Form(
        None, description="Whether the item is available"
    ),
    image: UploadFile = File(
        ...,
        description="New image file for the menu item (upload empty file to skip image update)",
    ),
    service: MenuService = Depends(MenuService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse[MenuItemUpdateResponse]:
    image_file = None
    if image and image.filename and image.size > 0:
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image"
            )

        if image.size and image.size > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image file too large. Maximum size is 5MB.",
            )

        image_content = await image.read()
        image_file = ContentFile(
            image_content,
            name=f"{category_slug}_{slug}_{uuid.uuid4().hex}.{image.filename.split('.')[-1]}",
        )

    request_data = MenuItemUpdateRequest(
        name=name, description=description, price=price, is_available=is_available
    )
    return BaseResponse(
        data=await service.update_menu_item(
            category_slug=category_slug,
            slug=slug,
            body=request_data,
            outlet=outlet,
            image_file=image_file,
        )
    )

@router.patch(
    "/{outlet_slug}/items/{category_slug}/{slug}/like",
    summary="Like Menu Item",
    description="""Like a menu item to increase its popularity score."""
)
@limiter.limit("1/minute")
async def like_menu_item(
    request: Request,
    category_slug: str,
    slug: str,
    service: MenuService = Depends(MenuService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse:
    """
    Like a menu item to increase its popularity score.

    Requires the user to be the admin of the outlet.
    """
    return BaseResponse(
        data=await service.like_menu_item(
            category_slug=category_slug, slug=slug
        )
    )

@router.patch(
    "/{outlet_slug}/items/{category_slug}/{slug}",
    summary="Update Menu Item (JSON)",
    description="""
    Update an existing menu item without image upload.

    Requires the user to be the admin of the outlet.

    Accepts application/json.
    """,
)
async def update_menu_item_json(
    category_slug: str,
    slug: str,
    data: MenuItemUpdateRequest,
    service: MenuService = Depends(MenuService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse[MenuItemUpdateResponse]:
    return BaseResponse(
        data=await service.update_menu_item(
            category_slug=category_slug,
            slug=slug,
            body=data,
            outlet=outlet,
            image_file=None,
        )
    )


@router.post(
    "/{outlet_slug}/items/upload-image/{category_slug}/{slug}",
    summary="Upload Menu Item Image",
    description="""
    Upload an image for an existing menu item.

    Requires the user to be the admin of the outlet.

    Accepts multipart/form-data with image file.
    """,
)
async def upload_menu_item_image(
    category_slug: str,
    slug: str,
    file: UploadFile = File(..., description="Image file to upload"),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse[dict]:
    # Validate image file
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image"
        )

    # Check file size (limit to 5MB)
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file too large. Maximum size is 5MB.",
        )

    try:
        category = await MenuCategory.objects.aget(slug=category_slug)

        item = await MenuItem.objects.aget(slug=slug, category=category)

        # Read the file content
        file_content = await file.read()

        # Generate filename using item slug
        file_extension = (
            file.filename.split(".")[-1]
            if file.filename and "." in file.filename
            else "jpg"
        )
        unique_filename = f"{item.slug}.{file_extension}"

        # Create Django ContentFile
        django_file = ContentFile(file_content, name=unique_filename)

        # Save the file to the model
        item.image.save(unique_filename, django_file, save=False)
        await item.asave()

        return BaseResponse(
            data={
                "message": "Image uploaded successfully",
                "image_url": item.image.url if item.image else None,
            }
        )
    except MenuCategory.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Menu category not found."
        )
    except MenuItem.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found."
        )


@router.post(
    "/{outlet_slug}/items/{category_slug}/rearrange_display_order",
    summary="Rearrange Menu Category Display Order",
    description="""
    Rearrange the display order of menu categories for an outlet.""",
)
async def rearrange_menu_item_display_order(
    data: ItemRearrangementRequest,
    category_slug: str,
    service: MenuService = Depends(MenuService),
    outlet=Depends(is_outlet_admin),
) -> BaseResponse[MenuItemObjects]:
    return BaseResponse(
        data=await service.rearrange_menu_item_display_order(
            body=data, category_slug=category_slug
        )
    )


@router.get(
    "/{outlet_slug}/items/search",
    summary="Search Menu Item",
    description="""
    Search for a menu category by slug."
    - ?query=search_term: Search term to filter categories by name or description.
    """,
)
async def search_menu_items(
    service: MenuService = Depends(MenuService),
    outlet=Depends(is_outlet_admin),
    category_slug: str = Query(
        ..., description="Slug of the category to search menu items in"
    ),
    query: str = Query(
        None, description="Search term to filter items by name or description"
    ),
    limit: Optional[int] = Query(10, description="Maximum number of items to return"),
) -> BaseResponse[MenuItemObjects]:
    return BaseResponse(
        data=await service.search_menu_items(
            category_slug=category_slug, query=query, limit=limit
        )
    )
