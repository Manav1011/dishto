from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, TokenBackendError
from django.conf import settings

security = HTTPBearer()
User = get_user_model()

async def verify_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
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
