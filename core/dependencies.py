from fastapi import Depends, HTTPException, Request, status, Path
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, TokenBackendError
from django.conf import settings
from core.utils.asyncs import get_related_object
from core.models import Outlet

User = get_user_model()

async def is_superadmin(request: Request):
    """
    Dependency to check if the user is a superadmin.
    Raises HTTPException if the user is not a superadmin.
    """    
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided.")
    if not user.is_superuser and not user.is_staff:
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")
    
    

async def is_franchise_admin(request: Request):
    """
    Dependency to check if the user is a franchise admin.
    Raises HTTPException if the user is not a franchise admin.
    """
    user = getattr(request.state, "user", None)
    franchise = getattr(request.state, "franchise", None)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided.")
    if not franchise:
        raise HTTPException(status_code=404, detail="Franchise not found.")
    admin = await get_related_object(franchise, "admin")
    if user.role != "franchise_owner" and admin != user:
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")
    return request.state.franchise

async def is_outlet_admin(request: Request, outlet_slug: str = Path(...)):    
    """
    Dependency to check if the user is an outlet admin.
    Raises HTTPException if the user is not an outlet admin.
    """
    user = getattr(request.state, "user", None)
    franchise = getattr(request.state, "franchise", None)    
    if not user:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided.")
    if not franchise:
        raise HTTPException(status_code=404, detail="Franchise not found.")
    try:
        outlet = await franchise.outlet_set.aget(slug=outlet_slug)
        admin = await get_related_object(outlet, "admin")
        if user.role != "outlet_owner" and admin != user:
            raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")   
    except Outlet.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outlet not found."
        )
    return outlet

def require_feature(feature_name: str):
    """
    Factory function to create a dependency that checks if the current outlet has a specific feature enabled.
    This dependency automatically resolves the outlet via `is_outlet_admin`.
    Raises HTTPException if the feature is not enabled for the outlet.
    """
    async def _feature_checker(outlet: Outlet = Depends(is_outlet_admin)) -> Outlet:
        # The M2M relation now points to GlobalFeature, so we check its name.
        if not await outlet.features.filter(name=feature_name).aexists():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature_name}' is not enabled for this outlet."
            )
        return outlet # Return the outlet if the feature is enabled

    return _feature_checker

async def franchise_exists(request: Request):
    """
    Dependency to check if the franchise exists.
    Raises HTTPException if the franchise does not exist.
    """    
    franchise = getattr(request.state, "franchise", None)
    if not franchise:
        raise HTTPException(status_code=404, detail="Franchise not found.")
    return franchise