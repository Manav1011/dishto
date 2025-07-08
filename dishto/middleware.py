from fastapi.middleware.cors import CORSMiddleware
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, TokenBackendError, TokenBackendExpiredToken
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
        self.public_paths = {
            '/docs', '/redoc', '/openapi.json'
        }

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        scope.setdefault("state", {})
        scope["state"]["user"] = None
        
        # Skip auth for public paths
        path = request.url.path
        if path in self.public_paths or path.startswith('/static/'):
            await self.app(scope, receive, send)
            return

        token = request.cookies.get("access")
        if token:
            try:
                decoded = self.token_backend.decode(token, verify=True)
                user_id = decoded.get("user_id")
                if user_id:
                    user = await User.objects.aget(id=user_id)
                    scope["state"]["user"] = user
            except (TokenBackendExpiredToken):
                # For expired tokens, just continue without user
                pass
            except (TokenError, InvalidToken, TokenBackendError):
                # For invalid tokens, remove the cookie
                response = JSONResponse(
                    {"detail": "Invalid token"}, 
                    status_code=401,
                    headers={"Set-Cookie": "access=; Path=/; Max-Age=0"}
                )
                await response(scope, receive, send)
                return
            except User.DoesNotExist:
                response = JSONResponse(
                    {"detail": "User not found"}, 
                    status_code=401,
                    headers={"Set-Cookie": "access=; Path=/; Max-Age=0"}
                )
                await response(scope, receive, send)
                return

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
        scope.setdefault("state", {})        
        if subdomain is not None:
            if subdomain != 'dev':
                try:
                    franchise = await Franchise.objects.aget(subdomain=subdomain)
                    scope["state"]["franchise"] = franchise
                except Franchise.DoesNotExist:                    
                    response = JSONResponse({"detail": "Franchise not found"}, status_code=404)
                    await response(scope, receive, send)
                    return
            else:
                request = Request(scope, receive=receive)
                test_cookie = request.cookies.get("dev")                
                if test_cookie == "true":
                    scope["state"]["franchise"] = await Franchise.objects.aget(slug='ce3e5b235d3a418a_1749737758950')
        if len(parts) == 1 and parts[0] == "localhost":            
            scope["state"]["franchise"] = await Franchise.objects.aget(slug='ce3e5b235d3a418a_1749737758950')
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