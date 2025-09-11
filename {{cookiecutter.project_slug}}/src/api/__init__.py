"""
API Package

Main API package for {{cookiecutter.project_name}}.
"""

from .factory import create_api, mount_api
from .router import router

__all__ = ["router", "create_api", "mount_api"]
