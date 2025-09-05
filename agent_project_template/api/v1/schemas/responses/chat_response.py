"""
Chat Response Schema
"""
from typing import Optional
from pydantic import Field
from .base_response import BaseResponse

class ChatResponse(BaseResponse):
    """
    Chat Response Schema
    
    继承自BaseResponse，自动包含：
    - session_id (str): 会话唯一标识（回传）
    - opaque (Optional[str]): 透传参数（回传）
    
    特有字段：
    - assistant_message (str): AI导师回复内容（流式输出）
    - request_id (str): 请求唯一标识（回传）
    - topic_id (Optional[str]): 当前回复聚焦的简历内容块 topic_id，若为 null 代表未聚焦特定内容块
    """
    assistant_message: str = Field(..., description="AI导师回复内容（流式输出）")
    request_id: str = Field(..., description="请求唯一标识（回传）")
    topic_id: Optional[str] = Field(None, description="当前回复聚焦的简历内容块 topic_id，若为 null 代表未聚焦特定内容块")
