from fastapi import Depends, HTTPException
from core.dependencies import verify_bearer_token

async def is_superadmin(user=Depends(verify_bearer_token)):
    """
    Dependency to check if the user is a superadmin.
    Raises HTTPException if the user is not a superadmin.
    """
    if not user.is_superuser and not user.is_staff:
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")
    return user