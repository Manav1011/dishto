from fastapi.middleware.cors import CORSMiddleware

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

    # Additional middleware can be added here if needed
    # Example: fastapi_app.add_middleware(SomeOtherMiddleware)