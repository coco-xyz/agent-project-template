"""
Generate Response Schema
"""
from pydantic import Field
from ai_agents.models.resume.resume_data import ResumeData
from .base_response import BaseResponse

class GenerateResponse(BaseResponse):
    """
    Generate Response Schema
    
    继承自BaseResponse，自动包含：
    - session_id (str): 会话唯一标识（回传）
    - opaque (Optional[str]): 透传参数（回传）
    
    特有字段：
    - resume (ResumeData): 完整的结构化简历数据
    - request_id (str): 请求唯一标识（回传）
    """
    resume: ResumeData = Field(..., description="完整的结构化简历数据")
    request_id: str = Field(..., description="请求唯一标识（回传）") 