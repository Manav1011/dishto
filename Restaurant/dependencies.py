from fastapi import Depends, HTTPException, Request

from .models import Franchise, MenuItem
from core.dependencies import verify_bearer_token

# async def is_franchise_admin(user = Depends(verify_bearer_token), slug: str = None):
#     """
#     Dependency to check if the user is a franchise admin.
#     Raises HTTPException if the user is not a franchise admin.
#     """
#     try:
#         franchise_obj = await Franchise.objects.aget(slug=slug)
#         if not franchise_obj.admin == user:
#             raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")
#         return user
#     except Franchise.DoesNotExist:
#         raise HTTPException(status_code=404, detail="Franchise not found.")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")

async def is_franchise_admin(user = Depends(verify_bearer_token)):
    """
    Dependency to check if the user is a franchise admin.
    Raises HTTPException if the user is not a franchise admin.
    """
    if user.role != "franchise_owner":
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")
    return user

async def is_outlet_admin(user = Depends(verify_bearer_token)):
    """
    Dependency to check if the user is an outlet admin.
    Raises HTTPException if the user is not an outlet admin.
    """
    if user.role != "outlet_owner":
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")
    return user