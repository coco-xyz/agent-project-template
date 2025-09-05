from typing import Optional
from pydantic import BaseModel, Field

class BaseResponse(BaseModel):
    """
    Base Response Schema
    
    所有响应类的基类，包含通用字段：
    - session_id (str): 会话唯一标识（雪花ID格式）
    - opaque (Optional[str]): 透传参数（回传）
    - error_code (int): 错误码，0表示成功，其他值表示错误
    - error_msg (str): 错误消息
    """
    session_id: str = Field(..., description="会话唯一标识（雪花ID格式）")
    opaque: Optional[str] = Field(None, description="透传参数（回传）")
    error_code: int = Field(default=0, description="错误码，0表示成功，其他值表示错误")
    error_msg: str = Field(default="Success", description="错误消息")
