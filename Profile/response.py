from pydantic import BaseModel

class TokenResponse(BaseModel):
    access: str
    refresh: str
    
class TokenRefreshResponse(BaseModel):
    access: str
    refresh: str
    
class SetPasswordResponse(BaseModel):
    email: str
    message: str = "Password has been set successfully."

class UpdateProfileResponse(BaseModel):
    name: str | None = None
    email: str | None = None
    ph_no: str | None = None
    message: str = "Profile updated successfully."