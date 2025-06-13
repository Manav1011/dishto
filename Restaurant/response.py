from pydantic import BaseModel

class FranchiseCreationResponse(BaseModel):
    name: str
    slug: str
    
class OutletCreationResponse(BaseModel):
    name: str
    slug: str