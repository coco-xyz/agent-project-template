"""
API Endpoints Package

FastAPI endpoint definitions for Agent Project Template.
"""

from .demo import router as demo_router
from .health import router as health_router

__all__ = ["demo_router", "health_router"]
