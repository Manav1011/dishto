from pydantic import BaseModel, constr

class FranchiseCreationRequest(BaseModel):
    name: constr(min_length=1, max_length=100) 

class OutletCreationRequest(BaseModel):
    name: constr(min_length=1, max_length=100) 
    franchise_slug: constr(min_length=1, max_length=100)
    