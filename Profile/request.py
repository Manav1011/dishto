from pydantic import BaseModel, EmailStr, constr, field_validator, ValidationError
from typing import Optional


class TokenRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=128)

    @field_validator("password")
    def validate_password(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class TokenRefreshRequest(BaseModel):
    refresh: constr(min_length=1)


class SetPasswordRequest(BaseModel):
    slug: constr(min_length=1, max_length=100)
    set_password_code: constr(min_length=1)
    new_password: constr(min_length=8, max_length=128)

    @field_validator("new_password")
    def validate_new_password(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v

class UpdatePasswordRequest(BaseModel):
    set_password_code: constr(min_length=1)
    new_password: constr(min_length=8, max_length=128)

    @field_validator("new_password")
    def validate_new_password(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class UpdateProfileRequest(BaseModel):
    name: Optional[constr(strip_whitespace=True, min_length=1)] = None
    email: Optional[EmailStr] = None
    ph_no: Optional[constr(strip_whitespace=True, min_length=5, max_length=15)] = None


class FranchiseAdminCreationRequest(BaseModel):
    email: EmailStr
    slug: constr(min_length=1, max_length=100)
    
class OutletAdminCreationRequest(BaseModel):
    email: EmailStr
    franchise_slug: constr(min_length=1, max_length=100)
    slug: constr(min_length=1, max_length=100)