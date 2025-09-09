"""
FastAPI router for the Agent Project Template API.

This module defines the main FastAPI router, including the version 1 router.
"""

from fastapi import APIRouter
from agent_project_template.api.v1 import router as v1_router

router = APIRouter()
router.include_router(v1_router, prefix="/v1")

__all__ = ["router"]
