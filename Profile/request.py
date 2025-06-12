from pydantic import BaseModel

class TokenRequest(BaseModel):
    email: str
    password: str
    
class TokenRefreshRequest(BaseModel):
    refresh: str