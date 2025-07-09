from .request import (
    CategoryRearrangementRequest,
    FranchiseCreationRequest,
    ItemRearrangementRequest,
    OutletCreationRequest,
    MenuCategoryCreationRequest,
    MenuCategoryUpdateRequest,
    MenuItemCreationRequest,
    MenuItemUpdateRequest
)

from .response import (
    MenuItemObjectsUser,
    MenuItemsContextualSearchResponse,
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
    MenuItemUpdateResponse,
    OutletObjectsUser
)
from .models import Franchise, Outlet, MenuCategory, MenuItem, CategoryImage
from fastapi import HTTPException, status
from core.utils.asyncs import get_related_object, get_queryset
from .utils import enhance_menu_item_description_with_ai, return_matching_menu_items, generate_menu_category_image
from django.contrib.postgres.search import SearchQuery

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
            
    async def get_franchise(self, slug: str, limit: int | None, last_seen_id: int | None) -> FranchiseObject | FranchiseObjects:
        if slug == "__all__":
            try:                            
                queryset = Franchise.objects.order_by("id")                
                if last_seen_id is not None:
                    queryset = queryset.filter(id__gt=last_seen_id)
                                                    
                if limit is not None:
                    queryset = queryset[:limit]

                franchises = await get_queryset(list, queryset)
                last_seen_id = franchises[-1].id if franchises else None
                return FranchiseObjects(
                    last_seen_id=last_seen_id,
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

    async def create_outlet(self, body: OutletCreationRequest, franchise) -> OutletCreationResponse:
        try:
            name = body.name
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
            
    async def get_outlet(self, slug: str, franchise, limit: int | None, last_seen_id: int | None) -> OutletObject | OutletObjects:
        try:                        
            if slug == "__all__":
                queryset = Outlet.objects.filter(franchise=franchise).order_by("id")
                if last_seen_id is not None:
                    queryset = queryset.filter(id__gt=last_seen_id)
                                                    
                if limit is not None:
                    queryset = queryset[:limit]

                outlets = await get_queryset(list, queryset)
                last_seen_id = outlets[-1].id if outlets else None                
                return OutletObjects(
                    last_seen_id=last_seen_id,
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
    async def create_menu_category(self, body: MenuCategoryCreationRequest, outlet) -> MenuCategoryCreationResponse:
        try:
            category = await MenuCategory.objects.acreate(
                name=body.name,
                outlet=outlet,
                description=body.description
            )
            # generte image for the category
            image = None
            try:
                image = await CategoryImage.objects.aget(category_name=category.name)
            except CategoryImage.DoesNotExist:
                # Generate image using AI
                image_content = await generate_menu_category_image(category.name)
                if image_content:
                    image = await CategoryImage.objects.acreate(
                        category_name=category.name,
                        image=image_content
                    )
                    category.image = image
                    await category.asave()
            return MenuCategoryCreationResponse(
                name=category.name,
                description=category.description,
                is_active=category.is_active,
                slug=category.slug,
                image=image.image.url if image else None
            )        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create menu category: {str(e)}"
            )

    async def get_menu_category(self, slug: str, outlet, limit: int | None, last_seen_order: int | None) -> MenuCategoryObject | MenuCategoryObjects:
        try:
            if slug == "__all__":
                queryset = MenuCategory.objects.filter(outlet=outlet).order_by("display_order")

                if last_seen_order is not None:                    
                    queryset = queryset.filter(display_order__gt=last_seen_order)
                                                    
                if limit is not None:
                    queryset = queryset[:limit]

                categories = await get_queryset(list, queryset)                
                last_seen_order = categories[-1].display_order if categories else None
                                
                categories_objs = []
                for c in categories:
                    img_obj = await get_related_object(c, "image")
                    image_url = img_obj.image.url if img_obj else None
                    categories_objs.append(
                        MenuCategoryObject(
                            name=c.name,
                            description=c.description or "",
                            is_active=c.is_active,
                            image=image_url,
                            slug=c.slug
                        )
                    )
                return MenuCategoryObjects(
                    last_seen_order=last_seen_order,
                    categories=categories_objs
                )
            else:
                try:
                    category = await MenuCategory.objects.aget(slug=slug, outlet=outlet)
                    img_obj = await get_related_object(category, "image")
                    image_url = img_obj.image.url if img_obj else None
                    return MenuCategoryObject(
                        name=category.name,
                        description=category.description or "",
                        is_active=category.is_active,
                        image=image_url,
                        slug=category.slug
                    )
                except MenuCategory.DoesNotExist:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Menu category not found."
                    )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve menu category: {str(e)}"
            )
    
    async def search_menu_categories(self, outlet, query: str, limit: int | None) -> MenuCategoryObjects:
        try:            
            # Perform search using the search vector
            queryset = MenuCategory.objects.filter(
                outlet=outlet,
                search_vector=SearchQuery(query)
            ).order_by("display_order")[:limit]
            
            categories = await get_queryset(list, queryset)
            if not categories:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No menu categories found matching the search query."
                )
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
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to search menu categories: {str(e)}"
            )

    async def update_menu_category(self,  slug: str, body: MenuCategoryUpdateRequest, outlet) -> MenuCategoryUpdateResponse:
        try:            
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

    async def delete_menu_category(self, slug: str, outlet):
        try:            
            category = await MenuCategory.objects.aget(slug=slug, outlet=outlet)
            await category.adelete()
            return {"message": "Menu category deleted successfully"}        
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
        
    async def rearrange_menu_category_display_order(self, body: CategoryRearrangementRequest, outlet) -> MenuCategoryObjects:
        try:
            mapping = {obj.category_slug: obj.display_order for obj in body.ordering}
            categories = await get_queryset(
                list,
                MenuCategory.objects.filter(slug__in=mapping.keys(), outlet=outlet)
            )
            
            found_slugs = {c.slug for c in categories}
            missing = set(mapping.keys()) - found_slugs
            if missing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu categories not found for slugs: {', '.join(missing)}"
                )

            for category in categories:
                category.display_order = mapping[category.slug]

            await MenuCategory.objects.abulk_update(categories, ["display_order"])

            # Return in new display order
            categories = sorted(categories, key=lambda c: c.display_order)
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
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update menu category display order: {str(e)}"
            )  
        
        
    
    async def create_menu_item(self, body: MenuItemCreationRequest, image_file=None) -> MenuItemCreationResponse:
        try:
            category = await MenuCategory.objects.aget(slug=body.category_slug)
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

    async def get_menu_item(self, category_slug: str, slug: str, outlet, limit, last_seen_order) -> MenuItemObject | MenuItemObjects:
        try:
            category = await MenuCategory.objects.aget(slug=category_slug)
            if slug == "__all__":
                queryset = MenuItem.objects.filter(category=category).order_by("display_order")

                if last_seen_order is not None:                    
                    queryset = queryset.filter(display_order__gt=last_seen_order)
                                                    
                if limit is not None:
                    queryset = queryset[:limit]

                items = await get_queryset(list, queryset)                
                last_seen_order = items[-1].display_order if items else None
                                
                return MenuItemObjects(
                    last_seen_order=last_seen_order,
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

    async def update_menu_item(self, category_slug: str, slug: str, body: MenuItemUpdateRequest, outlet, image_file=None) -> MenuItemUpdateResponse:
        try:
            category = await MenuCategory.objects.aget(slug=category_slug)
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

    async def delete_menu_item(self, category_slug: str, slug: str):
        try:
            category = await MenuCategory.objects.aget(slug=category_slug)
            outlet = await get_related_object(category, "outlet")
            admin = await get_related_object(outlet, "admin")            
            
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
            
    async def like_menu_item(self, category_slug: str, slug: str):
        try:
            category = await MenuCategory.objects.aget(slug=category_slug)
            item = await MenuItem.objects.aget(slug=slug, category=category)
            item.likes += 1
            await item.asave()
            return {"message": "Menu item liked successfully"}
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
                detail=f"Failed to like menu item: {str(e)}"
            )
            
    async def enhance_menu_item_description_with_ai(self, item_name: str, description: str) -> str:
        """
        Enhances the menu item description using AI.
        This method is a placeholder and should be implemented with actual AI logic.
        """
        # Placeholder for AI enhancement logic
        # In a real implementation, this would call an AI service to enhance the description
        
        return await enhance_menu_item_description_with_ai(item_name, description)
    
    async def rearrange_menu_item_display_order(self, body: ItemRearrangementRequest, category_slug: str) -> MenuItemObjects:
        try:
            category = await MenuCategory.objects.aget(slug=category_slug)
            mapping = {obj.menu_item_slug: obj.display_order for obj in body.ordering}
            items = await get_queryset(
                list,
                MenuItem.objects.filter(slug__in=mapping.keys(), category=category)
            )
            
            found_slugs = {i.slug for i in items}
            missing = set(mapping.keys()) - found_slugs
            if missing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu items not found for slugs: {', '.join(missing)}"
                )

            for item in items:
                item.display_order = mapping[item.slug]

            await MenuItem.objects.abulk_update(items, ["display_order"])

            # Return in new display order
            items = sorted(items, key=lambda i: i.display_order)
            return MenuItemObjects(
                items=[
                    MenuItemObject(
                        name=i.name,
                        description=i.description or "",
                        price=float(i.price),
                        is_available=i.is_available,
                        image=i.image.url if i.image else None,
                        slug=i.slug,
                        category_slug=category.slug
                    ) for i in items
                ]
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
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update menu item display order: {str(e)}"
            )
            
    async def search_menu_items(self, category_slug: str, query: str, limit: int | None) -> MenuItemObjects:
        try:
            category = await MenuCategory.objects.aget(slug=category_slug)
            
            # Perform search using the search vector
            queryset = MenuItem.objects.filter(
                category=category,
                search_vector=SearchQuery(query)
            ).order_by("display_order")[:limit]
            
            items = await get_queryset(list, queryset)
            if not items:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No menu items found matching the search query."
                )
            return MenuItemObjects(                    
                items=[
                    MenuItemObject(
                        name=i.name,
                        description=i.description or "",
                        price=float(i.price),
                        is_available=i.is_available,
                        image=i.image.url if i.image else None,
                        slug=i.slug,
                        category_slug=category.slug
                    ) for i in items
                ]
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

class UserRestaurantService:
    async def get_user_outlets(self, franchise) -> OutletObjectsUser:
        try:
            outlets = await get_queryset(
                list,
                franchise.outlet_set.all()
            )
            return OutletObjectsUser(
                outlets=[
                    OutletObject(name=o.name, slug=o.slug) for o in outlets
                ]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve user outlets: {str(e)}"
            )
            
    async def get_menu_for_outlet(self, franchise, outlet_slug: str) -> MenuItemObjectsUser:
        try:
            outlet = await franchise.outlet_set.aget(slug=outlet_slug)
            items = await get_queryset(
                list,
                MenuItem.objects.filter(category__outlet=outlet).order_by("category__display_order", "display_order")
            )
            return MenuItemObjectsUser(
                items=[
                    MenuItemObject(
                        name=item.name,
                        description=item.description or "",
                        price=float(item.price),
                        is_available=item.is_available,
                        image=item.image.url if item.image else None,
                        slug=item.slug,
                        category_slug=(await get_related_object(item, "category")).slug
                    ) for item in items
                ]
            )
        except Outlet.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Outlet not found."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve menu for outlet: {str(e)}"
            )
    async def search_menu_items_contextually(self, outlet_slug:str, query: str) -> MenuItemsContextualSearchResponse:
        try:
            # search directly in qdrant
            results = await return_matching_menu_items(
                query=query,
                outlet_slug=outlet_slug,
                limit=10
            )
            if not results:
                return MenuItemsContextualSearchResponse(items=[])
            seen = set()
            unique_slugs = []
            for item in results:
                slug = item['slug']
                if slug not in seen:
                    seen.add(slug)
                    unique_slugs.append(slug)
            return MenuItemsContextualSearchResponse(
                items=unique_slugs
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to search menu items: {str(e)}"
            )