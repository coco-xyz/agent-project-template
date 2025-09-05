"""
Core Package

Core configuration, error handling, and foundational components for AI Agents.
"""

from .config import Settings, settings
from .error_codes import (
    RequestParamErrorCode, AuthErrorCode, InternalServiceErrorCode, LLMCallErrorCode, DataProcessErrorCode, CallbackServiceErrorCode, DatabaseErrorCode,
    ERROR_CODE_MAP, HTTP_STATUS_MAP, get_error_code, get_http_status_code, get_error_info
)
from .exceptions import (
    RequestParamException, AuthException, InternalServiceException, LLMCallException, DataProcessException, CallbackServiceException,
    DatabaseException
)
from .exception_handlers import global_exception_handler
from .llm_factory import create_llm_model, create_fallback_model
from .prompt_loader import load_prompt
from .llm_registry import (
    get_gpt41_mini, get_gpt41, get_gpt5, get_gpt5_mini, get_gpt5_chat, get_gemini25_pro, get_claude4_sonnet, get_gemini25_flash_lite, get_gemini25_flash,
    get_gpt_oss_20b, get_gpt_oss_120b, get_grok_3_mini, get_grok_2_1212, get_kimi_k2, get_deepseek_chat_v31, get_glm_45
)
from ..stores.redis_client import RedisClient, get_redis_client, close_redis_client
from .database import Base, get_db, test_connection
from .empty_field_handler import EmptyFieldHandler
from .logfire_config import (
    initialize_logfire, setup_logfire, instrument_logfire, instrument_fastapi,
    is_logfire_enabled, get_logfire_service_name, get_logfire_environment,
    custom_request_attributes_mapper
)

__all__ = [
    # Configuration
    'Settings', 'settings',
    
    # Error handling
    'RequestParamErrorCode', 'AuthErrorCode', 'InternalServiceErrorCode', 'LLMCallErrorCode', 'DataProcessErrorCode', 'CallbackServiceErrorCode', 'DatabaseErrorCode',
    'ERROR_CODE_MAP', 'HTTP_STATUS_MAP', 'get_error_code', 'get_http_status_code', 'get_error_info',
    
    # Exceptions
    'RequestParamException', 'AuthException', 'InternalServiceException', 'LLMCallException', 'DataProcessException', 'CallbackServiceException',
    'DatabaseException',
    'global_exception_handler',
    
    # LLM Factory
    'create_llm_model', 'create_fallback_model',
    
    # LLM Registry (with integrated fallback support)
    'get_gpt41_mini', 'get_gpt41', 'get_gpt5', 'get_gpt5_mini', 'get_gpt5_chat', 'get_gemini25_pro', 'get_claude4_sonnet', 'get_gemini25_flash_lite', 'get_gemini25_flash',
    'get_gpt_oss_20b', 'get_gpt_oss_120b', 'get_grok_3_mini', 'get_grok_2_1212', 'get_kimi_k2', 'get_deepseek_chat_v31', 'get_glm_45',
    
    # Redis Client
    'RedisClient', 'get_redis_client', 'close_redis_client',
    
    # Database
    'Base', 'get_db', 'test_connection',
    
    # Utilities
    'load_prompt',
    'EmptyFieldHandler',
    
    # Logfire Configuration
    'initialize_logfire', 'setup_logfire', 'instrument_logfire', 'instrument_fastapi',
    'is_logfire_enabled', 'get_logfire_service_name', 'get_logfire_environment',
    'custom_request_attributes_mapper',
]
