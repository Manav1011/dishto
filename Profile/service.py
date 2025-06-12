from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework.exceptions import AuthenticationFailed
from fastapi import HTTPException, status
from dishto.utils.asyncs import is_valid_async
from .request import (
    TokenRequest,
    TokenRefreshRequest
)

from .response import (
    TokenResponse
)
class AuthService:
    async def obtain_token(self,body: TokenRequest):
        serializer = TokenObtainPairSerializer(data=body)
        try:
            if await is_valid_async(serializer):
                access = serializer.validated_data['access']
                refresh = serializer.validated_data['refresh']
                return TokenResponse(access=access, refresh=refresh)
        except AuthenticationFailed as e:            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )   
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            ) 
        