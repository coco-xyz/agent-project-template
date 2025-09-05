"""
Resume Parse Request Schema
"""
from pydantic import Field
from fastapi import UploadFile
from typing import Optional
from .base_request import BaseRequest

class ResumeParseRequest(BaseRequest):
    """
    Resume Parse Request Schema for file parsing
    
    字段说明：
    - request_id (str, 必填): 请求唯一标识 (继承自BaseRequest)
    - opaque (str, 可选): 透传参数 (继承自BaseRequest)
    - file (UploadFile, 必填): 待解析的简历文件(支持PDF、TXT格式)
    """
    file: UploadFile = Field(..., description="待解析的简历文件(支持PDF、TXT格式)") 