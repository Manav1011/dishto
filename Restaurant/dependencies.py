from fastapi import HTTPException, Request, Path, status
from core.utils.asyncs import get_related_object
from Restaurant.models import Outlet

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

async def franchise_exists(request: Request):
    """
    Dependency to check if the franchise exists.
    Raises HTTPException if the franchise does not exist.
    """
    franchise = getattr(request.state, "franchise", None)
    if not franchise:
        raise HTTPException(status_code=404, detail="Franchise not found.")
    return franchise