from fastapi import APIRouter, Depends

from core.schema import BaseResponse
from .service import AuthService
from .request import (
    TokenRequest,
    TokenRefreshRequest,
    SetPasswordRequest,
    UpdateProfileRequest
)

from .response import (
    TokenResponse,
    TokenRefreshResponse,
    SetPasswordResponse,
    UpdateProfileResponse
)
from core.dependencies import verify_bearer_token
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token")
async def obtain_token(data: TokenRequest, service: AuthService = Depends(AuthService)) -> BaseResponse[TokenResponse]:
    data = data.model_dump()
    return BaseResponse(data=await service.obtain_token(body=data))

        
@router.post("/refresh")
async def refresh_token(data: TokenRefreshRequest, service: AuthService = Depends(AuthService)) -> BaseResponse[TokenRefreshResponse]:
    data = data.model_dump()
    return BaseResponse(data=await service.refresh_token(body=data))

@router.post("/set-password")
async def set_password(
    data: SetPasswordRequest,
    service: AuthService = Depends(AuthService),
    user=Depends(verify_bearer_token)
) -> BaseResponse[SetPasswordResponse]:
    data = data.model_dump()
    return BaseResponse(data=await service.set_password(body=data, user=user))

@router.post("/update-profile")
async def update_profile(
    data: UpdateProfileRequest,
    service: AuthService = Depends(AuthService),
    user=Depends(verify_bearer_token)
) -> BaseResponse[UpdateProfileResponse]:
    data = data.model_dump()
    return BaseResponse(data=await service.update_profile(body=data, user=user))