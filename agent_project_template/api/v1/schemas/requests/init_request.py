"""
Init Request Schema
"""
from typing import Optional
from pydantic import Field, field_validator
from .base_request import BaseRequest
from ai_agents.models.resume.resume_data import ResumeData
from ai_agents.core.empty_field_handler import EmptyFieldHandler


class InitRequest(BaseRequest):
    """
    Init Request Schema for initializing AI Agent session

    字段说明：
    - resume_data (ResumeData, 必填): 简历初始数据，完整的简历数据结构
    - jd_content (str, 可选): 职位描述内容，用于AI导师针对性指导
    - request_id (str, 必填): 请求唯一标识 (继承自BaseRequest)
    - opaque (str, 可选): 透传参数 (继承自BaseRequest)

    注意：此接口对 resume_data 中的空字段采用宽松验证，空值会被自动填充为合理的默认值。
    """
    resume_data: ResumeData = Field(..., description="简历初始数据，完整的简历数据结构")
    jd_content: Optional[str] = Field(None, description="职位描述内容，用于AI导师针对性指导")
    
    @field_validator('resume_data', mode='before')
    @classmethod
    def handle_empty_fields(cls, v):
        """
        处理 resume_data 中的空字段，为空值填充合理的默认值
        
        Args:
            v: 原始的 resume_data 数据
            
        Returns:
            处理后的数据，空字段已填充默认值
        """
        return EmptyFieldHandler.fill_required_fields(v, ResumeData) 