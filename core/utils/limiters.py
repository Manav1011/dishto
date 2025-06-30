from slowapi import Limiter
from fastapi import Request
from slowapi.util import get_remote_address

def user_or_ip_key(request: Request) -> str:
    user = getattr(request.state, "user", None)    
    return str(user.slug)

limiter = Limiter(get_remote_address)