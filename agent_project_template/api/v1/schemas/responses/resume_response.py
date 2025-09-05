from typing import Optional
from pydantic import BaseModel, Field
from ai_agents.models.resume.resume_data import ResumeData

class ResumeResponse(BaseModel):
    """
    Resume response model

    """
    request_id: str = Field(..., description="请求ID")
    category: str = Field(default="RESUME", description="类别,固定为RESUME")
    content: Optional[ResumeData] = None
    opaque: Optional[str] = Field(None, description="透传参数（回传）")
    error_code: int = Field(default=0, description="错误码，0表示成功，其他值表示错误")
    error_msg: str = Field(default="Success", description="错误消息")