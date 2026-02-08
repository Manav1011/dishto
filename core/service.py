
from core.response import (    
    OutletObject,    
    OutletObjectsUser,
    OutletSliderImageObject,
    FranchiseObject,
    FranchiseObjects,    
    OutletCreationResponse,
    OutletObjects
)

from core.request import (
    FranchiseCreationRequest,
    OutletCreationRequest
)

from .models import Franchise, Outlet, OutletSliderImage
from fastapi import HTTPException, status
from core.utils.asyncs import get_queryset
from django.db.models import Prefetch


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

    async def create_outlet(self, body: OutletCreationRequest, franchise, cover_image=None, mid_page_slider=None) -> OutletCreationResponse:
        try:            
            name = body.name
            outlet = await Outlet.objects.acreate(
                name=name,
                franchise=franchise
            )
            # Save cover image if provided
            slider_objs = []
            if cover_image:
                outlet.cover_image.save(cover_image.name, cover_image, save=False)
                await outlet.asave()
            # Save slider images if provided
            if mid_page_slider:
                from .models import OutletSliderImage
                for idx, slider_file in enumerate(mid_page_slider):
                    slider_obj = await OutletSliderImage.objects.acreate(
                        outlet=outlet,
                        order=idx
                    )
                    slider_obj.image.save(slider_file.name, slider_file, save=False)
                    await slider_obj.asave()
                    slider_objs.append(slider_obj)
            # Prepare response
            from .response import OutletSliderImageObject
            slider_response = [OutletSliderImageObject(image=img.image.url, order=img.order) for img in slider_objs] if slider_objs else None
            return OutletCreationResponse(
                name=outlet.name,
                slug=str(outlet.slug) if outlet.slug else "",
                cover_image=outlet.cover_image.url if outlet.cover_image else None,
                mid_page_slider=slider_response
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
                outlet_objs = []
                for o in outlets:
                    slider_imgs = await get_queryset(list, OutletSliderImage.objects.filter(outlet=o).order_by("order"))
                    slider_response = [OutletSliderImageObject(image=img.image.url, order=img.order) for img in slider_imgs] if slider_imgs else None
                    outlet_objs.append(
                        OutletObject(
                            name=o.name,
                            slug=o.slug,
                            cover_image=o.cover_image.url if o.cover_image else None,
                            mid_page_slider=slider_response
                        )
                    )
                return OutletObjects(
                    last_seen_id=last_seen_id,
                    outlets=outlet_objs
                )
            else:
                try:
                    outlet = await Outlet.objects.aget(slug=slug, franchise=franchise)
                    slider_imgs = await get_queryset(list, OutletSliderImage.objects.filter(outlet=outlet).order_by("order"))
                    slider_response = [OutletSliderImageObject(image=img.image.url, order=img.order) for img in slider_imgs] if slider_imgs else None
                    return OutletObject(
                        name=outlet.name,
                        slug=outlet.slug,
                        cover_image=outlet.cover_image.url if outlet.cover_image else None,
                        mid_page_slider=slider_response
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
            
    # public
    async def get_user_outlets(self, franchise) -> OutletObjectsUser:
        try:            
            outlet_objs = []
            slider_prefetch = Prefetch("slider_images",queryset=OutletSliderImage.objects.order_by("order"))
            async for o in Outlet.objects.prefetch_related(slider_prefetch).filter(franchise=franchise):                
                slider_images = []
                async for img in o.slider_images.all():
                    slider_images.append(OutletSliderImageObject(image=img.image.url, order=img.order))
                outlet_objs.append(
                    OutletObject(
                        name=o.name,
                        slug=str(o.slug) if o.slug else "",
                        cover_image=o.cover_image.url if o.cover_image else None,
                        mid_page_slider=slider_images if slider_images else None
                    )
                )
            return OutletObjectsUser(
                outlets=outlet_objs
            )
        except Exception as e:            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve user outlets: {str(e)}"
            )