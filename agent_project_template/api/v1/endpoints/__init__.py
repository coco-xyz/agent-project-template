"""
API Endpoints Package

FastAPI endpoint definitions.
"""

from .demo import router as resume_router
from . import dependencies

__all__ = ["resume_router", "dependencies"] 