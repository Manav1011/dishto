from fastapi import status
from typing import Optional
from dishto.utils import constants

class CustomException(Exception):
    """
    Base custom exception class for raising necessary exceptions in the app.

    Attributes:
        status_code (int): The HTTP status code associated with the exception.
        message (str): The message associated with the exception.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    message = constants.SOMETHING_WENT_WRONG

    def __init__(self,status_code: status, message: Optional[str] = None):
        """
        Initialize the custom exception with an optional message.

        Args:
            message (Optional[str]): The message to be associated with the exception.
        """        
        self.message = message
        self.status_code = status_code

