"""
Init Response Schema
"""
from typing import Optional
from pydantic import Field
from .base_response import BaseResponse

class InitResponse(BaseResponse):
    """
    Init Response Schema

    继承自BaseResponse，自动包含：
    - session_id (str): 会话唯一标识（雪花ID格式）
    - opaque (Optional[str]): 透传参数（回传）

    新增字段：
    - jd_position (Optional[str]): 从JD内容中解析出来的职位名称
    - jd_company (Optional[str]): 从JD内容中解析出来的公司名称
    """
    jd_position: Optional[str] = Field(None, description="从JD内容中解析出来的职位名称")
    jd_company: Optional[str] = Field(None, description="从JD内容中解析出来的公司名称")