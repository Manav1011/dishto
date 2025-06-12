from pydantic import BaseModel
from typing import Generic, TypeVar
from dishto.utils import constants 
from pydantic.alias_generators import to_camel  # noqa
from fastapi import status as st


class CamelCaseModel(BaseModel):
    """
    A schemas for Camelcase.
    """

    class Config:
        """
        Configuration class for Pydantic models.
        This class defines configuration options for Pydantic models within the codebase. These options affect
        how the models are generated, validated, and populated.
        """

        alias_generator = to_camel
        populate_by_name = True
        arbitrary_types_allowed = True
        from_attributes = True

BaseDataField = TypeVar("BaseDataField")


class BaseResponse(CamelCaseModel, Generic[BaseDataField]):
    """
    Base response class for API responses.
    This class represents a base response structure for API responses. It includes fields for status, code,
    and data, which can be customized for specific responses.
    """

    status: str = constants.SUCCESS
    code: int = st.HTTP_200_OK
    data: BaseDataField | None = None
