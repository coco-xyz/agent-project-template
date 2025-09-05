"""
Generate Request Schema
"""
from pydantic import Field
from .base_request import BaseRequest


class GenerateRequest(BaseRequest):
    """
    Generate Request Schema for generating structured resume data
    
    字段说明：
    - request_id (str, 必填): 请求唯一标识 (继承自BaseRequest)
    - session_id (str, 必填): 会话唯一标识
    - opaque (str, 可选): 透传参数 (继承自BaseRequest)
    """
    session_id: str = Field(..., description="会话唯一标识") 