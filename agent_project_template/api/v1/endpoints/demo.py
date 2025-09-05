"""
Resume API Endpoints

FastAPI endpoints for resume-related operations.
"""

import json
from typing import Optional, Union

from fastapi import APIRouter, UploadFile, File, Form

# Request/Response schemas
from ai_agents.api.v1.schemas.requests import (
    InitRequest, ChatRequest, GenerateRequest,
    ResumeParseRequest, RawMarkdownRequest
)
from ai_agents.api.v1.schemas.responses import (
    InitResponse, GenerateResponse, ResumeParseResponse,
    JDResponse, ResumeResponse
)
from .dependencies import ResumeServiceDep
from sse_starlette import EventSourceResponse

router = APIRouter()


@router.post(
    "/init",
    response_model=InitResponse,
    summary="初始化AI导师简历构建会话",
    description="创建会话状态并建立初始话题队列，用于AI导师引导式简历构建",
    tags=["resume"]
)
async def init_session(
    request: InitRequest,
    service: ResumeServiceDep
):
    """
    Initialize AI Agent session for resume building.

    Args:
        request: InitRequest containing resume initial data and optional jd_content
        service: Resume service instance (injected)

    Returns:
        InitResponse: Session initialization result with session_id
    """
    session_result = await service.init_session(
        resume_data=request.resume_data,
        request_id=request.request_id,
        jd_content=request.jd_content
    )

    return InitResponse(
        session_id=session_result["session_id"],
        opaque=request.opaque,
        jd_position=session_result.get("jd_position"),
        jd_company=session_result.get("jd_company")
    )