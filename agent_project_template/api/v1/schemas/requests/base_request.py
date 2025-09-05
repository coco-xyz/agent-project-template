from pydantic import BaseModel, Field
from typing import Optional

class BaseRequest(BaseModel):
    """
    Base Request Schema
    """
    request_id: str = Field(..., description="请求ID")
    opaque: Optional[str] = Field(None, description="透传参数,包含task_id,batch_id等非必填项") 
    # callback_url: Optional[str] = Field(None, description="回调URL(非必填项)")