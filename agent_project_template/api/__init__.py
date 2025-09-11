"""
API Package

Main API package for Agent Project Template.
"""

from .factory import create_api, mount_api
from .router import router

__all__ = ["router", "create_api", "mount_api"]
