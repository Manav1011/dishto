from .request import (
    FranchiseCreationRequest,
    OutletCreationRequest
)

from .response import (
    FranchiseCreationResponse,
    OutletCreationResponse
)
from .models import Franchise, Outlet
from fastapi import HTTPException, status
from dishto.utils.asyncs import get_related_object

class RestaurantService:
    async def create_franchise(self, body: FranchiseCreationRequest):
        try:
            name = body.get('name',None)
            franchise = Franchise(name=name)
            await franchise.asave()
            return FranchiseCreationResponse(
                name=franchise.name,
                slug=franchise.slug
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create franchise: {str(e)}"
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