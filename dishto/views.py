from fastapi.responses import JSONResponse
from fastapi import status
import dishto.utils.constants as constants

def root() -> JSONResponse:
    """
    Root endpoint.

    Returns:
        JSONResponse: A JSON response with a success message.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": constants.SUCCESS}
    )

def healthcheck() -> JSONResponse:
    """
    Health check endpoint.
    
    Returns:
        JSONResponse: A JSON response with a success message.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": constants.SUCCESS}
    )