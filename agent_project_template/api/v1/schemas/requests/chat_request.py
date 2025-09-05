"""
Chat Request Schema
"""
from pydantic import Field
from .base_request import BaseRequest


class ChatRequest(BaseRequest):
    """
    Chat Request Schema for AI Agent conversation
    
    字段说明：
    - request_id (str, 必填): 请求唯一标识 (继承自BaseRequest)
    - session_id (str, 必填): 会话唯一标识
    - user_message (str, 必填): 用户输入内容
    - opaque (str, 可选): 透传参数 (继承自BaseRequest)
    """
    session_id: str = Field(..., description="会话唯一标识")
    user_message: str = Field(..., description="用户输入内容") 