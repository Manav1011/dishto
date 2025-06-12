from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework.exceptions import AuthenticationFailed
from fastapi import HTTPException, status
from dishto.GlobalUtils import generate_unique_hash
from dishto.utils.asyncs import is_valid_async
from .request import (
    TokenRequest,
    TokenRefreshRequest
)
from .response import (
    TokenResponse,
    TokenRefreshResponse,
    SetPasswordResponse,
    UpdateProfileResponse
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
    async def refresh_token(self, body: TokenRefreshRequest):
        serializer = TokenRefreshSerializer(data=body)
        try:
            if await is_valid_async(serializer):
                print(serializer.validated_data)
                return TokenRefreshResponse(**serializer.validated_data)
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
        
    async def set_password(self, body: dict, user):
        """
        Set a new password for the user.
        :param body: Dictionary containing the new password and other necessary fields.
        :param user: The user object for whom the password is being set.
        :return: TokenResponse with access and refresh tokens.
        """
        password = body.get('new_password')
        set_password_code = body.get('set_password_code')
        if user.forgot_password_code != set_password_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid password reset code.')
        user.set_password(password)
        user.forgot_password_code = generate_unique_hash()
        await user.asave()
        return SetPasswordResponse(email=user.email)
    
    
    async def update_profile(self, body: dict, user):
        """
        Update the user's profile information.
        :param body: Dictionary containing the updated profile information.
        :param user: The user object whose profile is being updated.
        :return: UpdateProfileResponse with the updated profile information.
        """
        user.name = body.get('name') or user.name
        user.email = body.get('email') or user.email
        user.ph_no = body.get('ph_no') or user.ph_no
        await user.asave()
        return UpdateProfileResponse(name=user.name, email=user.email, ph_no=user.ph_no)