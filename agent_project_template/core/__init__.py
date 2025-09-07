"""
Core Package

Core configuration, error handling, and foundational components for AI Agents.
"""
# ruff: noqa: F401  # All imports are re-exported via __all__

from .config import Settings, settings  # noqa: F401
from .error_codes import (  # noqa: F401
    RequestParamErrorCode, AuthErrorCode, InternalServiceErrorCode, LLMErrorCode,
    DataProcessErrorCode, CallbackServiceErrorCode, DatabaseErrorCode,
    ERROR_CODE_MAP, get_http_status_code, get_error_info
)
from .exceptions import (  # noqa: F401
    ApplicationException,
    RequestParamException, AuthException, InternalServiceException, LLMCallException,
    DataProcessException, CallbackServiceException, DatabaseException
)
from .llm_factory import create_llm_model, create_fallback_model  # noqa: F401
from .prompt_loader import load_prompt  # noqa: F401
from .llm_registry import (  # noqa: F401
    get_demo_model, get_default_model, get_fallback_model,
    list_available_models, get_model_by_name
)
from .logger import get_logger  # noqa: F401
from .logfire_config import (  # noqa: F401
    initialize_logfire, setup_logfire, instrument_logfire, instrument_fastapi,
    is_logfire_enabled, get_logfire_service_name, get_logfire_environment,
    custom_request_attributes_mapper
)

__all__ = [
    # Configuration
    'Settings', 'settings',

    # Error handling
    'RequestParamErrorCode', 'AuthErrorCode', 'InternalServiceErrorCode', 'LLMErrorCode',
    'DataProcessErrorCode', 'CallbackServiceErrorCode', 'DatabaseErrorCode',
    'ERROR_CODE_MAP', 'get_http_status_code', 'get_error_info',

    # Exceptions
    'ApplicationException',
    'RequestParamException', 'AuthException', 'InternalServiceException', 'LLMCallException',
    'DataProcessException', 'CallbackServiceException', 'DatabaseException',

    # LLM Factory
    'create_llm_model', 'create_fallback_model',

    # LLM Registry
    'get_demo_model', 'get_default_model', 'get_fallback_model',
    'list_available_models', 'get_model_by_name',

    # Utilities
    'load_prompt',

    # Logger
    'get_logger',

    # Logfire Configuration
    'initialize_logfire', 'setup_logfire', 'instrument_logfire', 'instrument_fastapi',
    'is_logfire_enabled', 'get_logfire_service_name', 'get_logfire_environment',
    'custom_request_attributes_mapper',
]
