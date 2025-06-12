from pydantic import BaseModel

class FranchiseCreationResponse(BaseModel):
    name: str
    slug: str