"""
Submit Request Schema
"""
from pydantic import Field
from .base_request import BaseRequest

class SubmitRequest(BaseRequest):
    """
    Submit Request Schema for combined file parsing and structured output
    """
    category: str = Field(..., description="类别,如RESUME或JD", min_length=1, max_length=20) 