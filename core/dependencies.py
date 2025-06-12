from fastapi import Header, HTTPException, status
from typing import Annotated

# auth

def verify_bearer_token(authorization: Annotated[str | None, Header()] = None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    
    token = authorization.removeprefix("Bearer ").strip()
    return token
