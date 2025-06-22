from pydantic import BaseModel

class FranchiseObject(BaseModel):
    name: str
    slug: str

class FranchiseObjects(BaseModel):
    franchises: list[FranchiseObject]
    
class FranchiseCreationResponse(BaseModel):
    name: str
    slug: str
    
class OutletCreationResponse(BaseModel):
    name: str
    slug: str
    
class OutletObject(BaseModel):
    name: str
    slug: str
    
class OutletObjects(BaseModel):
    outlets: list[OutletObject]