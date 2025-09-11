"""
API Endpoints Package

FastAPI endpoint definitions for {{cookiecutter.project_name}}.
"""

from .demo import router as demo_router
from .health import router as health_router

__all__ = ["demo_router", "health_router"]
