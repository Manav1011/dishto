from fastapi import FastAPI
from django.conf import settings
from dishto.utils.lifespan import lifespan
from dishto.middleware import setup_middleware
from dishto.utils.schema import BaseValidationResponse
from dishto.urls import base_router


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

    setup_middleware(fastapi_app)
    
    fastapi_app.include_router(base_router, responses={422: {"model": BaseValidationResponse}})
    return fastapi_app