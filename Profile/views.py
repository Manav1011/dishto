from fastapi import APIRouter, HTTPException, status, Request, Depends
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from core.schema import BaseResponse
from .service import AuthService
from .request import (
    TokenRequest,
    TokenRefreshRequest
)

from .response import (
    TokenResponse
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token")
async def obtain_token(data: TokenRequest, service: AuthService = Depends(AuthService)) -> BaseResponse[TokenResponse]:
    data = data.model_dump()
    return BaseResponse(data=await service.obtain_token(body=data))

        
@router.post("/refresh")
async def refresh_token(data: TokenRefreshRequest):
    serializer = TokenRefreshSerializer(data=data.dict())
    if serializer.is_valid():
        return serializer.validated_data
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=serializer.errors
        )
