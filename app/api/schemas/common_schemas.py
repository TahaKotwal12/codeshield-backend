from pydantic import BaseModel
from typing import TypeVar, Generic, Optional

# Generic type for response data
T = TypeVar('T')

class CommonResponse(BaseModel, Generic[T]):
    """
    Standard response format for all CodeShield API endpoints.
    """
    code: int
    message: str
    message_id: str
    data: T

class CommonHeaders(BaseModel):
    """
    Common headers for CodeShield API requests.
    """
    pass

def get_common_headers() -> CommonHeaders:
    """
    Dependency to get common headers.
    """
    return CommonHeaders()


