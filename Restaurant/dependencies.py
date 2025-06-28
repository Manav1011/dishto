from fastapi import HTTPException, Request

async def is_franchise_admin(request: Request):
    """
    Dependency to check if the user is a franchise admin.
    Raises HTTPException if the user is not a franchise admin.
    """
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided.")
    if user.role != "franchise_owner":
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")
    return user

async def is_outlet_admin(request: Request):
    """
    Dependency to check if the user is an outlet admin.
    Raises HTTPException if the user is not an outlet admin.
    """
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided.")
    if user.role != "outlet_owner":
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")
    return user