from .request import (
    FranchiseCreationRequest,
    OutletCreationRequest,
    MenuCategoryCreationRequest,
    MenuCategoryUpdateRequest,
    MenuItemCreationRequest,
    MenuItemUpdateRequest
)

from .response import (
    OutletCreationResponse,
    FranchiseObject,
    FranchiseObjects,
    OutletObject,
    OutletObjects,
    MenuCategoryCreationResponse,
    MenuCategoryObject,
    MenuCategoryObjects,
    MenuCategoryUpdateResponse,
    MenuItemCreationResponse,
    MenuItemObject,
    MenuItemObjects,
    MenuItemUpdateResponse
)
from .models import Franchise, Outlet, MenuCategory, MenuItem
from fastapi import HTTPException, status
from core.utils.asyncs import get_related_object, get_queryset
from django.core.files.base import ContentFile
import uuid

class RestaurantService:
    async def create_franchise(self, body: FranchiseCreationRequest):
        try:
            name = body.name
            franchise = Franchise(name=name)
            await franchise.asave()
            return FranchiseObject(
                name=franchise.name,
                slug=franchise.slug
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create franchise: {str(e)}"
            )
            
    async def get_franchise(self, slug: str) -> FranchiseObject | FranchiseObjects:
        if slug == "__all__":
            try:
                franchises = await get_queryset(list, Franchise.objects.all())
                return FranchiseObjects(
                    franchises=[
                        FranchiseObject(name=f.name, slug=f.slug) for f in franchises
                    ]
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to retrieve franchises: {str(e)}"
                )
        else:
            try:
                franchise = await Franchise.objects.aget(slug=slug)
                return FranchiseObject(
                    name=franchise.name,
                    slug=franchise.slug
                )
            except Franchise.DoesNotExist:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Franchise not found."
                )

    async def create_outlet(self, body: OutletCreationRequest, user) -> OutletCreationResponse:
        try:
            name = body.name
            franchise_slug = body.franchise_slug
            franchise = await Franchise.objects.aget(slug=franchise_slug)
            admin = await get_related_object(franchise, "admin")
            if admin != user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to create an outlet for this franchise."
                )
            outlet = await Outlet.objects.acreate(
                name=name,
                franchise=franchise
            )
            return OutletCreationResponse(
                name=outlet.name,
                slug=outlet.slug
            )
        except Franchise.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Franchise does not exist."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create outlet: {str(e)}"
            )
            
    async def get_outlet(self, franchise_slug: str, slug: str, user) -> OutletObject | OutletObjects:
        try:
            franchise = await Franchise.objects.aget(slug=franchise_slug)
            admin = await get_related_object(franchise, "admin")
            if admin != user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this outlet."
                )
            if slug == "__all__":
                outlets = await get_queryset(list, Outlet.objects.filter(franchise=franchise))
                return OutletObjects(
                    outlets=[
                        OutletObject(name=o.name, slug=o.slug) for o in outlets
                    ]
                )
            else:
                try:
                    outlet = await Outlet.objects.aget(slug=slug, franchise=franchise)
                    return OutletObject(
                        name=outlet.name,
                        slug=outlet.slug
                    )
                except Outlet.DoesNotExist:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Outlet not found."
                    )
        except Franchise.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Franchise not found."
            )
            
class MenuService:
    async def create_menu_category(self, body: MenuCategoryCreationRequest, user) -> MenuCategoryCreationResponse:
        try:
            outlet = await Outlet.objects.aget(slug=body.outlet)
            admin = await get_related_object(outlet, "admin")
            if admin != user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to create a menu category for this outlet."
                )
            category = await MenuCategory.objects.acreate(
                name=body.name,
                outlet=outlet,
                description=body.description
            )
            return MenuCategoryCreationResponse(
                name=category.name,
                description=category.description,
                is_active=category.is_active,
                slug=category.slug
            )
        except Outlet.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Outlet not found."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create menu category: {str(e)}"
            )

    async def get_menu_category(self, outlet_slug: str, slug: str, user) -> MenuCategoryObject | MenuCategoryObjects:
        try:
            outlet = await Outlet.objects.aget(slug=outlet_slug)
            admin = await get_related_object(outlet, "admin")
            if admin != user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access menu categories for this outlet."
                )
            
            if slug == "__all__":
                categories = await get_queryset(list, MenuCategory.objects.filter(outlet=outlet))
                return MenuCategoryObjects(
                    categories=[
                        MenuCategoryObject(
                            name=c.name,
                            description=c.description or "",
                            is_active=c.is_active,
                            slug=c.slug
                        ) for c in categories
                    ]
                )
            else:
                try:
                    category = await MenuCategory.objects.aget(slug=slug, outlet=outlet)
                    return MenuCategoryObject(
                        name=category.name,
                        description=category.description or "",
                        is_active=category.is_active,
                        slug=category.slug
                    )
                except MenuCategory.DoesNotExist:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Menu category not found."
                    )
        except Outlet.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Outlet not found."
            )

    async def update_menu_category(self, outlet_slug: str, slug: str, body: MenuCategoryUpdateRequest, user) -> MenuCategoryUpdateResponse:
        try:
            outlet = await Outlet.objects.aget(slug=outlet_slug)
            admin = await get_related_object(outlet, "admin")
            if admin != user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to update menu categories for this outlet."
                )
            
            category = await MenuCategory.objects.aget(slug=slug, outlet=outlet)
            
            # Update fields if provided
            if body.name is not None:
                category.name = body.name
            if body.description is not None:
                category.description = body.description
            if body.is_active is not None:
                category.is_active = body.is_active
            
            await category.asave()
            
            return MenuCategoryUpdateResponse(
                name=category.name,
                description=category.description or "",
                is_active=category.is_active,
                slug=category.slug
            )
        except Outlet.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Outlet not found."
            )
        except MenuCategory.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu category not found."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update menu category: {str(e)}"
            )

    async def delete_menu_category(self, outlet_slug: str, slug: str, user):
        try:
            outlet = await Outlet.objects.aget(slug=outlet_slug)
            admin = await get_related_object(outlet, "admin")
            if admin != user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to delete menu categories for this outlet."
                )
            
            category = await MenuCategory.objects.aget(slug=slug, outlet=outlet)
            await category.adelete()
            
            return {"message": "Menu category deleted successfully"}
        except Outlet.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Outlet not found."
            )
        except MenuCategory.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu category not found."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete menu category: {str(e)}"
            )
    
    async def create_menu_item(self, body: MenuItemCreationRequest, user, image_file=None) -> MenuItemCreationResponse:
        try:
            category = await MenuCategory.objects.aget(slug=body.category_slug)
            outlet = await get_related_object(category, "outlet")
            admin = await get_related_object(outlet, "admin")
            if admin != user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to create menu items for this outlet."
                )
            
            # Create menu item
            item = await MenuItem.objects.acreate(
                name=body.name,
                category=category,
                description=body.description,
                price=body.price,
                is_available=body.is_available
            )
            
            # Handle image upload if provided
            image_url = None
            if image_file:                                
                # Generate filename using item slug
                file_extension="png"
                unique_filename = f"{item.slug}.{file_extension}"
                
                image_file.name = unique_filename  # Set the name for the ContentFile            
                
                # Save the file to the model
                item.image.save(unique_filename, image_file, save=False)
                await item.asave()
                image_url = item.image.url if item.image else None
            
            return MenuItemCreationResponse(
                name=item.name,
                description=item.description or "",
                price=float(item.price),
                is_available=item.is_available,
                image=image_url,
                slug=item.slug,
                category_slug=category.slug
            )
        except MenuCategory.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu category not found."
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create menu item: {str(e)}"
            )

    async def get_menu_item(self, category_slug: str, slug: str, user) -> MenuItemObject | MenuItemObjects:
        try:
            category = await MenuCategory.objects.aget(slug=category_slug)
            outlet = await get_related_object(category, "outlet")
            admin = await get_related_object(outlet, "admin")
            if admin != user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access menu items for this outlet."
                )
            
            if slug == "__all__":
                items = await get_queryset(list, MenuItem.objects.filter(category=category))
                return MenuItemObjects(
                    items=[
                        MenuItemObject(
                            name=item.name,
                            description=item.description or "",
                            price=float(item.price),
                            is_available=item.is_available,
                            image=item.image.url if item.image else None,
                            slug=item.slug,
                            category_slug=category.slug
                        ) for item in items
                    ]
                )
            else:
                try:
                    item = await MenuItem.objects.aget(slug=slug, category=category)
                    return MenuItemObject(
                        name=item.name,
                        description=item.description or "",
                        price=float(item.price),
                        is_available=item.is_available,
                        image=item.image.url if item.image else None,
                        slug=item.slug,
                        category_slug=category.slug
                    )
                except MenuItem.DoesNotExist:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Menu item not found."
                    )
        except MenuCategory.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu category not found."
            )

    async def update_menu_item(self, category_slug: str, slug: str, body: MenuItemUpdateRequest, user, image_file=None) -> MenuItemUpdateResponse:
        try:
            category = await MenuCategory.objects.aget(slug=category_slug)
            outlet = await get_related_object(category, "outlet")
            admin = await get_related_object(outlet, "admin")
            if admin != user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to update menu items for this outlet."
                )
            
            item = await MenuItem.objects.aget(slug=slug, category=category)
            
            # Update fields if provided
            if body.name is not None:
                item.name = body.name
            if body.description is not None:
                item.description = body.description
            if body.price is not None:
                item.price = body.price
            if body.is_available is not None:
                item.is_available = body.is_available
            
            # Handle image upload if provided
            if image_file:
                # image_file is already a Django ContentFile, so we can save it directly
                item.image.save(image_file.name, image_file, save=False)
            
            # Save the item
            await item.asave()
            
            return MenuItemUpdateResponse(
                name=item.name,
                description=item.description or "",
                price=float(item.price),
                is_available=item.is_available,
                image=item.image.url if item.image else None,
                slug=item.slug,
                category_slug=category.slug
            )
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
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update menu item: {str(e)}"
            )

    async def delete_menu_item(self, category_slug: str, slug: str, user):
        try:
            category = await MenuCategory.objects.aget(slug=category_slug)
            outlet = await get_related_object(category, "outlet")
            admin = await get_related_object(outlet, "admin")
            if admin != user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to delete menu items for this outlet."
                )
            
            item = await MenuItem.objects.aget(slug=slug, category=category)
            
            # Delete the image file if it exists
            if item.image:
                try:
                    item.image.delete(save=False)
                except:
                    pass  # Continue even if image deletion fails
            
            await item.adelete()
            
            return {"message": "Menu item deleted successfully"}
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
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete menu item: {str(e)}"
            )