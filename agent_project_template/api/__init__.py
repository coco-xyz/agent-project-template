"""
API Package

Main API package for Agent Project Template.
"""

from .router import router
from .factory import create_api, mount_api

__all__ = ["router", "create_api", "mount_api"]
