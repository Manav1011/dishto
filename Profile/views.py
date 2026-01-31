from fastapi import APIRouter, Depends, Request, Response

from core.schema import BaseResponse
from .service import AuthService, AdminCreation, UserInfoService
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
    FranchiseAdminCreationResponse,
    UserInfoResponse
)

from core.dependencies import is_superadmin
from Restaurant.dependencies import is_franchise_admin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def obtain_token(data: TokenRequest, service: AuthService = Depends(AuthService)) -> Response:
    """
    Asynchronously obtains authentication tokens and sets them as HTTP-only cookies in the response.

    Args:
        data (TokenRequest): The request data containing authentication credentials.
        service (AuthService, optional): The authentication service dependency. Defaults to Depends(AuthService).

    Returns:
        Response: An HTTP response containing the serialized tokens in the body and the access/refresh tokens as cookies.

    Notes:
        - The cookies are set with 'httponly', 'secure', and 'samesite' attributes for security.
        - The 'samesite' attribute is set to "lax". Other valid options for 'samesite' are:
            - "strict": Cookies are only sent for same-site requests.
            - "none": Cookies are sent in all contexts, including cross-site requests (requires 'secure' to be True).
            - "lax": Cookies are sent for same-site requests and top-level navigation GET requests from other sites.
    """
    data = data.model_dump()
    tokens = await service.obtain_token(body=data)
    response = Response(content=tokens.model_dump_json(), media_type="application/json")
    response.set_cookie(
        key="access",
        value=tokens.access,
        httponly=True,
        secure=True,
        samesite="none",
    )
    response.set_cookie(
        key="refresh",
        value=tokens.refresh,
        httponly=True,
        secure=True,
        samesite="none"        
    )
    return response

@router.post("/logout")
async def logout() -> Response:
    response = Response(content='{"message": "Logged out successfully"}', media_type="application/json")
    # Remove both cookies
    response.delete_cookie(
        key="access",
        httponly=True,
        secure=True,
        samesite="lax",
        path="/"
    )
    response.delete_cookie(
        key="refresh",
        httponly=True,
        secure=True,
        samesite="lax",
        path="/"
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

@router.get("/user-info")
async def get_user_info(
    request: Request,
    service: UserInfoService = Depends(UserInfoService)
) -> BaseResponse[UserInfoResponse]:    
        user = request.state.user
        return BaseResponse(data = await service.get_user_info(user))

@router.post("/set-password")
async def set_password(
    data: SetPasswordRequest,
    service: AuthService = Depends(AuthService)
) -> BaseResponse[SetPasswordResponse]:    
    return BaseResponse(data=await service.set_password(body=data))


@router.post("/update-password")
async def update_password(
    request: Request,
    data: UpdatePasswordRequest,
    service: AuthService = Depends(AuthService),    
) -> BaseResponse[UpdatePasswordResponse]:
    if not request.state.user:
        return BaseResponse(status_code=401, message="Authentication credentials were not provided.")    
    return BaseResponse(data=await service.update_password(body=data, user=request.state.user))

@router.post("/update-profile")
async def update_profile(
    request: Request,
    data: UpdateProfileRequest,
    service: AuthService = Depends(AuthService),    
) -> BaseResponse[UpdateProfileResponse]:
    if not request.state.user:
        return BaseResponse(status_code=401, message="Authentication credentials were not provided.")    
    return BaseResponse(data=await service.update_profile(body=data, user=request.state.user))

@router.post("/admin/franchise", dependencies=[Depends(is_superadmin)])
async def create_franchise_admin(data: FranchiseAdminCreationRequest, service: AdminCreation = Depends(AdminCreation)) -> BaseResponse[FranchiseAdminCreationResponse]:
    """
    Create a new franchise admin (super super admin only).
    """
    return BaseResponse(data=await service.create_franchise_admin(body=data))

@router.post("/admin/outlet")
async def create_outlet_admin(
    data: OutletAdminCreationRequest,
    service: AdminCreation = Depends(AdminCreation),
    franchise=Depends(is_franchise_admin)
) -> BaseResponse[OutletAdminCreationResponse]:
    """
    Create a new outlet admin (franchise admin only).
    """
    return BaseResponse(data=await service.create_outlet_admin(body=data, franchise=franchise))