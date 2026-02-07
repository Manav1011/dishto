from fastapi import FastAPI
from django.conf import settings
from core.utils.lifespan import lifespan
from dishto.middleware import setup_middleware
from core.utils.schema import BaseValidationResponse
from dishto.urls import base_router_protected, base_router_open
from core.utils.limiters import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

def get_fastapi_application() -> FastAPI:
    """
    Initializes and configures a FastAPI application instance.

    This function creates a FastAPI app with custom settings, including title, version,
    documentation URLs, and Swagger UI parameters. It also sets up middleware and healthcheck routes.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    fastapi_app = FastAPI(
        title=settings.APP_NAME,
        root_path="/api",
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc" if settings.DEBUG else None,
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True,
            "tryItOutEnabled": True,
            "requestSnippetsEnabled": True,
            "withCredentials": True,
            "persistAuthorization": True,
        },
        lifespan=lifespan,
    )
    
    fastapi_app.state.limiter = limiter
    fastapi_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    setup_middleware(fastapi_app)
    
    from scalar_fastapi import get_scalar_api_reference, Theme

    @fastapi_app.get("/scalar-docs", include_in_schema=False)
    async def scalar_docs():
        return get_scalar_api_reference(
            openapi_url="/openapi.json",
            title="My API Docs",
            theme=Theme.MARS,            
            persist_auth=True,
            telemetry=True,
            expand_all_responses=True,
        )
    fastapi_app.include_router(base_router_open, responses={422: {"model": BaseValidationResponse}})
    fastapi_app.include_router(base_router_protected, responses={422: {"model": BaseValidationResponse}})
    return fastapi_app