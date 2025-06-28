from fastapi import Depends, HTTPException, Request
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, TokenBackendError
from django.conf import settings
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