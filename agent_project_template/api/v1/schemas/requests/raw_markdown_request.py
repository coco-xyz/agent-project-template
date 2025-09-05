from typing import Optional
from pydantic import Field
from .base_request import BaseRequest

class RawMarkdownRequest(BaseRequest):
    """
    Raw markdown content request model
    
    字段说明：
    - request_id (str, 必填): 请求唯一标识 (继承自BaseRequest)
    - opaque (str, 可选): 透传参数 (继承自BaseRequest)
    - category (str, 必填): 类别，如RESUME或JD
    - content (str, 必填): 原始内容
    """
    category: str = Field(..., description="类别,如RESUME或JD", min_length=1, max_length=20)
    content: str = Field(..., description="原始内容", min_length=1, max_length=50000)