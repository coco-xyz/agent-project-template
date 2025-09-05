"""
API Version 1 Package

Version 1 of the API endpoints and schemas.
"""

from fastapi import APIRouter
from .endpoints import resume_router

router = APIRouter()
router.include_router(resume_router, prefix="/resume", tags=["resume"])
__all__ = ["router"]
