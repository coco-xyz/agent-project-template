"""
Resume Parse Response Schema
"""
from pydantic import Field
from typing import Optional
from .base_response import BaseResponse

class ResumeParseResponse(BaseResponse):
    """
    Resume Parse Response Schema
    
    继承自BaseResponse，自动包含：
    - session_id (str): 会话唯一标识（雪花ID格式）
    - opaque (Optional[str]): 透传参数（回传）
    - error_code (int): 错误码，0表示成功，其他值表示错误
    - error_msg (str): 错误消息
    
    特有字段：
    - request_id (str): 请求ID
    - data (str): 处理结果数据，即解析出的纯文本内容
    """
    request_id: str = Field(..., description="请求ID")
    data: str = Field(..., description="处理结果数据，即解析出的纯文本内容") 