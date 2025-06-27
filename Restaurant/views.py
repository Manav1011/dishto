from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from typing import Optional
import uuid

from Restaurant.response import OutletCreationResponse
from core.schema import BaseResponse

from .request import FranchiseCreationRequest, OutletCreationRequest, MenuCategoryCreationRequest, MenuCategoryUpdateRequest, MenuItemCreationRequest, MenuItemUpdateRequest
from .response import FranchiseObject, FranchiseObjects, OutletObject, OutletObjects, MenuCategoryCreationResponse, MenuCategoryObject, MenuCategoryObjects, MenuCategoryUpdateResponse, MenuItemCreationResponse, MenuItemObject, MenuItemObjects, MenuItemUpdateResponse
from .service import RestaurantService, MenuService
from .models import MenuCategory, MenuItem
from dishto.utils.asyncs import get_related_object
from django.core.files.base import ContentFile
from core.dependencies import is_superadmin
from .dependencies import is_franchise_admin, is_outlet_admin

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
    return BaseResponse(data = await service.create_franchise(body=data))

@router.get("/franchise/{slug}", summary="Get Franchise", description="Retrieve a franchise by slug.", dependencies=[Depends(is_superadmin)])
async def get_franchise(slug: str, service: RestaurantService = Depends(RestaurantService)) -> BaseResponse[FranchiseObject | FranchiseObjects]:
    """Retrieve a franchise by slug."""
    return BaseResponse(data = await service.get_franchise(slug=slug))


@router.post("/outlet", summary="Create Outlet", description="Create a new outlet for the restaurant service.")
async def create_outlet(data: OutletCreationRequest, service: RestaurantService = Depends(RestaurantService), user=Depends(is_franchise_admin)) -> BaseResponse[OutletCreationResponse]:
    """
    Create a new outlet.
    """
    # Placeholder logic for creating an outlet
    return BaseResponse(data = await service.create_outlet(body=data, user=user))

@router.get("/outlet/{franchise_slug}/{slug}", summary="Get Outlet", description="Retrieve an outlet by slug.")
async def get_outlet(franchise_slug: str, slug: str, service: RestaurantService = Depends(RestaurantService), user=Depends(is_franchise_admin)) -> BaseResponse[OutletObject | OutletObjects]:
    """Retrieve an outlet by slug."""
    return BaseResponse(data = await service.get_outlet(franchise_slug=franchise_slug, slug=slug, user=user))

@router.post("/categories", summary="Create Menu Category", description="Create a new menu category for the outlet")
async def create_menu_category(data: MenuCategoryCreationRequest, service: MenuService = Depends(MenuService), user=Depends(is_outlet_admin)) -> BaseResponse[MenuCategoryCreationResponse]:
    """
    Create a new menu category.
    """
    return BaseResponse(data = await service.create_menu_category(body=data, user=user))

@router.get("/categories/{outlet_slug}/{slug}", summary="Get Menu Category", description="Retrieve menu categories by outlet and slug (use '__all__' for all categories)")
async def get_menu_category(outlet_slug: str, slug: str, service: MenuService = Depends(MenuService), user=Depends(is_outlet_admin)) -> BaseResponse[MenuCategoryObject | MenuCategoryObjects]:
    """
    Retrieve menu categories by outlet slug and category slug.
    Use '__all__' as slug to get all categories for the outlet.
    """
    return BaseResponse(data = await service.get_menu_category(outlet_slug=outlet_slug, slug=slug, user=user))

@router.put("/categories/{outlet_slug}/{slug}", summary="Update Menu Category", description="Update an existing menu category")
async def update_menu_category(outlet_slug: str, slug: str, data: MenuCategoryUpdateRequest, service: MenuService = Depends(MenuService), user=Depends(is_outlet_admin)) -> BaseResponse[MenuCategoryUpdateResponse]:
    """
    Update an existing menu category.
    """
    return BaseResponse(data = await service.update_menu_category(outlet_slug=outlet_slug, slug=slug, body=data, user=user))

@router.delete("/categories/{outlet_slug}/{slug}", summary="Delete Menu Category", description="Delete a menu category")
async def delete_menu_category(outlet_slug: str, slug: str, service: MenuService = Depends(MenuService), user=Depends(is_outlet_admin)) -> BaseResponse[dict]:
    """
    Delete a menu category.
    """
    return BaseResponse(data = await service.delete_menu_category(outlet_slug=outlet_slug, slug=slug, user=user))

# Menu Item APIs
@router.post("/items", summary="Create Menu Item", description="Create a new menu item for a category")
async def create_menu_item(
    *,
    name: str = Form(..., description="Name of the menu item"),
    category_slug: str = Form(..., description="Slug of the menu category"),
    description: str = Form(..., description="Description of the menu item"),
    price: float = Form(..., description="Price of the menu item"),
    is_available: bool = Form(True, description="Whether the item is available"),
    image: UploadFile = File(..., description="Image file for the menu item"),
    service: MenuService = Depends(MenuService),
    user=Depends(is_outlet_admin)
) -> BaseResponse[MenuItemCreationResponse]:
    """
    Create a new menu item with image upload.
    Content-Type: multipart/form-data
    """
    # Validate image file
    if not image.content_type or not image.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Check file size (limit to 5MB)
    if image.size and image.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file too large. Maximum size is 5MB."
        )
    
    # Create request object from form data
    request_data = MenuItemCreationRequest(
        name=name,
        category_slug=category_slug,
        description=description,
        price=price,
        is_available=is_available
    )
    return BaseResponse(data = await service.create_menu_item(body=request_data, user=user, image_file=image))

@router.post("/items/no-image", summary="Create Menu Item (No Image)", description="Create a new menu item without image")
async def create_menu_item_no_image(
    data: MenuItemCreationRequest, 
    service: MenuService = Depends(MenuService), 
    user=Depends(is_outlet_admin)
) -> BaseResponse[MenuItemCreationResponse]:
    """
    Create a new menu item without image upload.
    Content-Type: application/json
    """
    return BaseResponse(data = await service.create_menu_item(body=data, user=user, image_file=None))

@router.get("/items/{category_slug}/{slug}", summary="Get Menu Item", description="Retrieve menu items by category and slug (use '__all__' for all items)")
async def get_menu_item(category_slug: str, slug: str, service: MenuService = Depends(MenuService), user=Depends(is_outlet_admin)) -> BaseResponse[MenuItemObject | MenuItemObjects]:
    """
    Retrieve menu items by category slug and item slug.
    Use '__all__' as slug to get all items for the category.
    """
    return BaseResponse(data = await service.get_menu_item(category_slug=category_slug, slug=slug, user=user))

@router.put("/items/{category_slug}/{slug}", summary="Update Menu Item", description="Update an existing menu item. To skip image update, upload an empty file or a file with no name.")
async def update_menu_item(
    category_slug: str, 
    slug: str,
    *,
    name: Optional[str] = Form(None, description="Name of the menu item"),
    description: Optional[str] = Form(None, description="Description of the menu item"),
    price: Optional[float] = Form(None, description="Price of the menu item"),
    is_available: Optional[bool] = Form(None, description="Whether the item is available"),
    image: UploadFile = File(..., description="New image file for the menu item (upload empty file to skip image update)"),
    service: MenuService = Depends(MenuService),
    user=Depends(is_outlet_admin)
) -> BaseResponse[MenuItemUpdateResponse]:
    """
    Update an existing menu item with optional image upload.
    Content-Type: multipart/form-data
    """
    # Validate image file if provided - skip if empty file or no filename
    image_file = None
    if image and image.filename and image.size > 0:
        # Check if it's actually an image
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Check file size (limit to 5MB)
        if image.size and image.size > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image file too large. Maximum size is 5MB."
            )
        
        # Convert UploadFile to Django ContentFile
        image_content = await image.read()
        image_file = ContentFile(image_content, name=f"{category_slug}_{slug}_{uuid.uuid4().hex}.{image.filename.split('.')[-1]}")
    
    # Create request object from form data
    request_data = MenuItemUpdateRequest(
        name=name,
        description=description,
        price=price,
        is_available=is_available
    )
    return BaseResponse(data = await service.update_menu_item(category_slug=category_slug, slug=slug, body=request_data, user=user, image_file=image_file))

@router.patch("/items/{category_slug}/{slug}", summary="Update Menu Item (JSON)", description="Update menu item without image")
async def update_menu_item_json(
    category_slug: str, 
    slug: str,
    data: MenuItemUpdateRequest,
    service: MenuService = Depends(MenuService),
    user=Depends(is_outlet_admin)
) -> BaseResponse[MenuItemUpdateResponse]:
    """
    Update an existing menu item without image upload.
    Content-Type: application/json
    """
    return BaseResponse(data = await service.update_menu_item(category_slug=category_slug, slug=slug, body=data, user=user, image_file=None))

# Alternative file upload endpoint
@router.post("/items/upload-image/{category_slug}/{slug}", summary="Upload Menu Item Image", description="Upload image for existing menu item")
async def upload_menu_item_image(
    category_slug: str,
    slug: str,
    file: UploadFile = File(..., description="Image file to upload"),
    user=Depends(is_outlet_admin)
) -> BaseResponse[dict]:
    """
    Upload an image for an existing menu item.
    This is a pure file upload endpoint.
    """
    # Validate image file
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Check file size (limit to 5MB)
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file too large. Maximum size is 5MB."
        )
    
    try:
        category = await MenuCategory.objects.aget(slug=category_slug)
        outlet = await get_related_object(category, "outlet")
        admin = await get_related_object(outlet, "admin")
        if admin != user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to upload images for this outlet."
            )
        
        item = await MenuItem.objects.aget(slug=slug, category=category)
        
        # Read the file content
        file_content = await file.read()
        
        # Generate filename using item slug
        file_extension = file.filename.split('.')[-1] if file.filename and '.' in file.filename else 'jpg'
        unique_filename = f"{item.slug}.{file_extension}"
        
        # Create Django ContentFile
        django_file = ContentFile(file_content, name=unique_filename)
        
        # Save the file to the model
        item.image.save(unique_filename, django_file, save=False)
        await item.asave()
        
        return BaseResponse(data={"message": "Image uploaded successfully", "image_url": item.image.url if item.image else None})
    except MenuCategory.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu category not found."
        )
    except MenuItem.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found."
        )
