"""
FastAPI router for the AI Agents API.

This module defines the FastAPI router for the AI Agents API, including the version 1 router.
"""

from fastapi import APIRouter
from ai_agents.api.v1 import router as v1_router

router = APIRouter()
router.include_router(v1_router, prefix="/v1")
__all__ = ["router"] 