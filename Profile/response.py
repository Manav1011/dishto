from pydantic import BaseModel

class TokenResponse(BaseModel):
    access: str
    refresh: str
    message: str = "Logged in successfully."
    
class TokenRefreshResponse(BaseModel):
    access: str
    refresh: str

class SetPasswordResponse(BaseModel):
    email: str
    message: str = "Password has been set successfully."

class UpdatePasswordResponse(BaseModel):
    email: str
    message: str = "Password has been updated successfully."

class UpdateProfileResponse(BaseModel):
    name: str | None = None
    email: str | None = None
    ph_no: str | None = None
    message: str = "Profile updated successfully."
    
    
class FranchiseAdminCreationResponse(BaseModel):
    email: str
    role: str = "franchise_admin"
    message: str = "Franchise admin created successfully."
    
class OutletAdminCreationResponse(BaseModel):
    email: str
    role: str = "outlet_admin"
    message: str = "Outlet admin created successfully."
    
class UserInfoResponse(BaseModel):
    email: str | None = None
    name: str | None = None
    ph_no: str | None = None
    role: str | None = None
    slug: str | None = None