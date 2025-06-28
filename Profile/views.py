from fastapi import APIRouter, Depends, Request, Response

from core.schema import BaseResponse
from .service import AuthService, AdminCreation
from .request import (
    FranchiseAdminCreationRequest,
    OutletAdminCreationRequest,
    TokenRequest,
    TokenRefreshRequest,
    SetPasswordRequest,
    UpdatePasswordRequest,
    UpdateProfileRequest
)

from .response import (
    OutletAdminCreationResponse,
    TokenRefreshResponse,
    SetPasswordResponse,
    UpdatePasswordResponse,
    UpdateProfileResponse,
    FranchiseAdminCreationResponse
)

from core.dependencies import is_superadmin
from Restaurant.dependencies import is_franchise_admin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token")
async def obtain_token(data: TokenRequest, service: AuthService = Depends(AuthService)) -> Response:
    data = data.model_dump()
    tokens = await service.obtain_token(body=data)
    response = Response(content=tokens.model_dump_json(), media_type="application/json")
    response.set_cookie(
        key="access",
        value=tokens.access,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    response.set_cookie(
        key="refresh",
        value=tokens.refresh,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    return response

        
@router.post("/refresh")
async def refresh_token(request: Request, service: AuthService = Depends(AuthService)) -> BaseResponse[TokenRefreshResponse]:
    refresh_token = request.cookies.get("refresh")
    if not refresh_token:
        return BaseResponse(status_code=401, message="Missing refresh token")
    body = TokenRefreshRequest(refresh=refresh_token).model_dump()
    tokens=await service.refresh_token(body=body)
    response = Response(content=tokens.model_dump_json(), media_type="application/json")
    response.set_cookie(
        key="access",
        value=tokens.access,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    response.set_cookie(
        key="refresh",
        value=tokens.refresh,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    return response

@router.post("/set-password")
async def set_password(
    data: SetPasswordRequest,
    service: AuthService = Depends(AuthService)
) -> BaseResponse[SetPasswordResponse]:
    data = data.model_dump()
    return BaseResponse(data=await service.set_password(body=data))


@router.post("/update-password")
async def update_password(
    request: Request,
    data: UpdatePasswordRequest,
    service: AuthService = Depends(AuthService),    
) -> BaseResponse[UpdatePasswordResponse]:
    if not request.state.user:
        return BaseResponse(status_code=401, message="Authentication credentials were not provided.")
    data = data.model_dump()
    return BaseResponse(data=await service.update_password(body=data, user=request.state.user))

@router.post("/update-profile")
async def update_profile(
    request: Request,
    data: UpdateProfileRequest,
    service: AuthService = Depends(AuthService),    
) -> BaseResponse[UpdateProfileResponse]:
    if not request.state.user:
        return BaseResponse(status_code=401, message="Authentication credentials were not provided.")
    data = data.model_dump()
    return BaseResponse(data=await service.update_profile(body=data, user=request.state.user))

@router.post("/admin/franchise", dependencies=[Depends(is_superadmin)])
async def create_franchise_admin(data: FranchiseAdminCreationRequest, service: AdminCreation = Depends(AdminCreation)) -> BaseResponse[FranchiseAdminCreationResponse]:
    """
    Create a new franchise admin (super super admin only).
    """
    return BaseResponse(data=await service.create_franchise_admin(body=data.model_dump()))

@router.post("/admin/outlet")
async def create_outlet_admin(
    data: OutletAdminCreationRequest,
    service: AdminCreation = Depends(AdminCreation),
    user=Depends(is_franchise_admin)
) -> BaseResponse[OutletAdminCreationResponse]:
    """
    Create a new outlet admin (franchise admin only).
    """
    return BaseResponse(data=await service.create_outlet_admin(body=data.model_dump(), user=user))