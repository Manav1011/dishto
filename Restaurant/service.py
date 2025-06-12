from .request import (
    FranchiseCreationRequest
)

from .response import (
    FranchiseCreationResponse
)
from .models import Franchise
from fastapi import HTTPException, status

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