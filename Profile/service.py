import django
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework.exceptions import AuthenticationFailed
from fastapi import HTTPException, status
from Restaurant.models import Franchise, Outlet

from dishto.GlobalUtils import generate_unique_hash
from core.utils.asyncs import is_valid_async
from .request import (
    TokenRequest,
    TokenRefreshRequest
)
from .response import (
    OutletAdminCreationResponse,
    TokenResponse,
    TokenRefreshResponse,
    SetPasswordResponse,
    UpdateProfileResponse,
    FranchiseAdminCreationResponse
)
import traceback
from core.models import User
from core.utils.asyncs import get_related_object

class AuthService:
    async def obtain_token(self,body: TokenRequest):
        serializer = TokenObtainPairSerializer(data=body)
        try:
            if await is_valid_async(serializer):
                access = serializer.validated_data['access']
                refresh = serializer.validated_data['refresh']
                return TokenResponse(access=access, refresh=refresh, message="Logged in successfully.")
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
    
    async def set_password(self, body: dict):
        slug = body.get('slug')
        set_password_code = body.get('set_password_code')
        password = body.get('new_password')
        
        try:
            user = await User.objects.aget(slug=slug)
            if user.forgot_password_code != set_password_code:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid password reset code.')
            user.set_password(password)
            user.forgot_password_code = generate_unique_hash()
            await user.asave()
            return SetPasswordResponse(email=user.email)
        except User.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found.'
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Error retrieving user: {str(e)}'
            )
        
    async def update_password(self, body: dict, user):
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
    
    
class AdminCreation:
    async def create_franchise_admin(self, body: dict) -> FranchiseAdminCreationResponse:
        email = body.get("email")
        slug = body.get("slug")
        try:
            franchise_object = await Franchise.objects.aget(slug=slug)
            user_obj = await User.objects.acreate(
                email=email,
                role="franchise_owner"
            )
            franchise_object.admin = user_obj
            await franchise_object.asave()
            return FranchiseAdminCreationResponse(
                email=user_obj.email,
                role=user_obj.role,
                message="Franchise admin created successfully."
            )
        except django.db.utils.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email {email} already exists."
            )
        except Franchise.DoesNotExist:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Franchise does not exist."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create franchise admin: {str(e)}"
            )
    
    async def create_outlet_admin(self, body: dict, user) -> OutletAdminCreationResponse:
        email = body.get("email")
        franchise_slug = body.get("franchise_slug")
        slug = body.get("slug")
        try:
            franchise_object = await Franchise.objects.aget(slug=franchise_slug)
            admin = await get_related_object(franchise_object, "admin")
            if admin != user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to create an outlet admin for this franchise."
                )
            outlet_object = await Outlet.objects.aget(slug=slug, franchise=franchise_object)
            user_obj = await User.objects.acreate(
                email=email,
                role="outlet_owner"
            )
            outlet_object.admin = user_obj
            await outlet_object.asave()
            return OutletAdminCreationResponse(
                email=user_obj.email,
                role=user_obj.role,
                message="Outlet admin created successfully."
            )
            
        except django.db.utils.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email {email} already exists."
            )
        except Franchise.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Franchise does not exist."
            )
        except Outlet.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Outlet does not exist."
            )
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create outlet admin: {str(e)}"
            )