from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, TokenBackendError
from django.conf import settings
User = get_user_model()

async def verify_bearer_token(request: Request):
    token = request.cookies.get("access")
    if not token:
        raise HTTPException(status_code=401, detail="Missing credentials")
    try:
        decoded = TokenBackend(algorithm='HS256', signing_key=settings.SECRET_KEY).decode(token, verify=True)
        user_id = decoded.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: no user ID")
        user = await User.objects.aget(id=user_id)
        return user
    except (TokenError, InvalidToken, TokenBackendError):
        raise HTTPException(status_code=401, detail="Invalid token")
    except User.DoesNotExist:
        raise HTTPException(status_code=401, detail="User not found")

async def is_superadmin(user=Depends(verify_bearer_token)):
    """
    Dependency to check if the user is a superadmin.
    Raises HTTPException if the user is not a superadmin.
    """
    if not user.is_superuser and not user.is_staff:
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")
    return user