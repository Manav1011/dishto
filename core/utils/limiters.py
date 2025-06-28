from slowapi.util import get_remote_address
from slowapi import Limiter
from fastapi import Request


def user_or_ip_key(request: Request) -> str:
    user = getattr(request.state, "user", None)    
    return str(user.slug)

auth_limiter = Limiter(key_func=user_or_ip_key)