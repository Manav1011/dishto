from .request import (
    FranchiseCreationRequest,
    OutletCreationRequest
)

from .response import (
    OutletCreationResponse,
    FranchiseObject,
    FranchiseObjects,
    OutletObject,
    OutletObjects
)
from .models import Franchise, Outlet
from fastapi import HTTPException, status
from dishto.utils.asyncs import get_related_object, get_queryset

class RestaurantService:
    async def create_franchise(self, body: FranchiseCreationRequest):
        try:
            name = body.get('name',None)
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
            name = body.get('name', None)
            franchise_slug = body.get('franchise_slug', None)
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