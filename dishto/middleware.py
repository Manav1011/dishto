from fastapi.middleware.cors import CORSMiddleware
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, TokenBackendError
from django.conf import settings
from fastapi import HTTPException, Request
from Restaurant.models import Franchise
from starlette.responses import JSONResponse
from starlette.types import Scope, Receive, Send


User = get_user_model()

class AuthMiddleware:
    def __init__(self, app):
        self.app = app
        self.token_backend = TokenBackend(
            algorithm='HS256',
            signing_key=settings.SECRET_KEY
        )

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)        
        scope["state"]["user"] = None

        token = request.cookies.get("access")
        if token:
            try:
                decoded = self.token_backend.decode(token, verify=True)
                user_id = decoded.get("user_id")
                if user_id:
                    user = await User.objects.aget(id=user_id)
                    scope["state"]["user"] = user
            except (TokenError, InvalidToken, TokenBackendError):
                raise HTTPException(status_code=401, detail="Invalid token")
            except User.DoesNotExist:
                raise HTTPException(status_code=401, detail="User not found")

        await self.app(scope, receive, send)

class FranchiseMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope["headers"])
        host = headers.get(b"host", b"").decode("latin-1").split(":")[0]  # remove port if present
        parts = host.split(".")
        subdomain = parts[0] if len(parts) > 2 else None
        if subdomain != 'dev':
            try:
                franchise = await Franchise.objects.aget(subdomain=subdomain)            
                scope.setdefault("state", {})
                scope["state"]["franchise"] = franchise
            except Franchise.DoesNotExist:
                response = JSONResponse({"detail": "Franchise not found"}, status_code=404)
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)


def setup_middleware(fastapi_app) -> None:
    """Set up middleware for the FastAPI application."""
    # Add CORS middleware
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins, adjust as needed
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods, adjust as needed
        allow_headers=["*"],  # Allow all headers, adjust as needed
    )
    fastapi_app.add_middleware(FranchiseMiddleware)
    fastapi_app.add_middleware(AuthMiddleware)
    # Additional middleware can be added here if needed
    # Example: fastapi_app.add_middleware(SomeOtherMiddleware)