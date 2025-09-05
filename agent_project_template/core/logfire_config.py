"""
Logfire Configuration Module

Centralized logfire configuration and instrumentation setup for AI Agents project.
This module provides reusable functions for setting up logfire monitoring that can be
used across the application and in tests.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request

from ai_agents.core.config import settings
from ai_agents.utils.logger import setup_logfire_handler

# Global state to track initialization
_logfire_configured = False
_logfire_instrumented = False


def _custom_scrub_callback(match):
    """
    Custom scrubbing callback that allows session_id fields while keeping other protections.

    Args:
        match: ScrubMatch object containing path, value, and pattern_match

    Returns:
        The original value if it should be kept, None if it should be redacted
    """
    # Get the path as a tuple of keys
    path = match.path

    # Allow session_id fields (don't redact them)
    if any('session_id' in str(part).lower() for part in path):
        return match.value

    # Allow sid fields (our custom session tag format)
    if any('sid' in str(part).lower() for part in path):
        return match.value

    # For all other matches, use default behavior (redact)
    return None


def custom_request_attributes_mapper(request: Request, attributes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Custom request attributes mapper for logfire.
    
    This function customizes what information gets logged for each request.
    It filters sensitive information and focuses on useful debugging data.
    
    Args:
        request: The FastAPI request object
        attributes: Default attributes dictionary from logfire
        
    Returns:
        dict or None: Customized attributes dict, or None to set span level to 'debug'
    """
    # Always log validation errors as they're important for debugging
    if attributes.get("errors"):
        return {
            "errors": attributes["errors"],
            "endpoint": str(request.url.path),
            "method": request.method,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "request_id": request.headers.get("x-request-id"),
        }
    
    # For successful requests, log basic info but hide sensitive data
    filtered_values = {}
    session_id = None

    if attributes.get("values"):
        for key, value in attributes["values"].items():
            # Explicitly preserve session_id fields
            if key.lower() in ["session_id", "sid"]:
                filtered_values[key] = value
                session_id = value
            # Filter out sensitive information
            elif key.lower() in ["password", "token", "api_key", "secret"]:
                filtered_values[key] = "[REDACTED]"
            elif key == "file" and hasattr(value, "filename"):
                # For file uploads, just log filename and size
                filtered_values[key] = {
                    "filename": getattr(value, "filename", "unknown"),
                    "content_type": getattr(value, "content_type", "unknown"),
                    "size": getattr(value, "size", 0) if hasattr(value, "size") else "unknown"
                }
            else:
                filtered_values[key] = value

    result = {
        "values": filtered_values,
        "endpoint": str(request.url.path),
        "method": request.method,
        "request_id": request.headers.get("x-request-id"),
    }

    # Explicitly add session_id at the top level if found
    if session_id:
        result["session_id"] = session_id

    return result


def setup_logfire() -> bool:
    """
    Set up basic logfire configuration.
    
    Returns:
        bool: True if logfire was successfully configured, False otherwise
    """
    global _logfire_configured
    
    if not settings.logfire__enabled or _logfire_configured:
        return _logfire_configured
        
    try:
        import logfire
        
        config_kwargs = {
            "service_name": settings.logfire__service_name,
            "environment": settings.logfire__environment,
        }

        # Configure scrubbing to allow session_id fields
        if settings.logfire__disable_scrubbing:
            # Completely disable scrubbing if explicitly requested
            config_kwargs["scrubbing"] = False
        else:
            # Use custom scrubbing options to allow session_id while keeping other protections
            try:
                config_kwargs["scrubbing"] = logfire.ScrubbingOptions(
                    callback=_custom_scrub_callback
                )
            except (AttributeError, TypeError) as e:
                # Fallback: if ScrubbingOptions is not available or API changed
                logging.warning(f"ScrubbingOptions not available or API changed: {e}")
                logging.warning("Falling back to disabled scrubbing")
                config_kwargs["scrubbing"] = True
        
        if settings.logfire__token:
            config_kwargs["token"] = settings.logfire__token
            # print("Logfire token provided, enabling authentication: %s...", settings.logfire__token[:16])
            
        # Note: sample_rate is commented out as it's not supported in current version
        # if settings.logfire__sample_rate is not None:
        #     try:
        #         config_kwargs["sample_rate"] = settings.logfire__sample_rate
        #     except TypeError:
        #         logging.warning("sample_rate parameter not supported in this logfire version")
        
        logfire.configure(**config_kwargs)
        print(f"Logfire initialized for service: {settings.logfire__service_name}")
        
        # Set up Logfire logging handler after configuration
        setup_logfire_handler()
        
        _logfire_configured = True
        return True
        
    except Exception as e:
        print(f"Failed to initialize logfire: {e}")
        return False


def instrument_logfire() -> Dict[str, bool]:
    """
    Set up logfire instrumentation for various libraries.
    
    Returns:
        dict: Dictionary with instrumentation results for each library
    """
    global _logfire_instrumented
    
    results = {
        "pydantic_ai": False,
        "redis": False,
        "httpx": False
    }
    
    if not settings.logfire__enabled or _logfire_instrumented:
        return results
    
    try:
        import logfire
        
        # Instrument pydantic-ai
        try:
            logfire.instrument_pydantic_ai()
            print("Logfire pydantic-ai instrumentation enabled")
            results["pydantic_ai"] = True
        except Exception as e:
            print(f"Failed to instrument pydantic-ai with logfire: {e}")
        
        # Instrument Redis
        try:
            logfire.instrument_redis()
            print("Logfire Redis instrumentation enabled")
            results["redis"] = True
        except Exception as e:
            print(f"Failed to instrument Redis with logfire: {e}")
        
        # Instrument HTTPX
        try:
            logfire.instrument_httpx(capture_all=True)
            print("Logfire HTTPX instrumentation enabled")
            results["httpx"] = True
        except Exception as e:
            print(f"Failed to instrument HTTPX with logfire: {e}")
            
        _logfire_instrumented = True
            
    except ImportError:
        print("Logfire not available for instrumentation")
    except Exception as e:
        print(f"Failed to set up logfire instrumentation: {e}")
    
    return results


def instrument_fastapi(app: FastAPI) -> bool:
    """
    Set up logfire instrumentation for FastAPI.
    
    Args:
        app: The FastAPI application instance
        
    Returns:
        bool: True if FastAPI was successfully instrumented, False otherwise
    """
    if not settings.logfire__enabled:
        return False
    
    try:
        import logfire
        
        logfire.instrument_fastapi(
            app, 
            request_attributes_mapper=custom_request_attributes_mapper,
            capture_headers=True
        )
        print("FastAPI instrumented with logfire")
        return True
        
    except Exception as e:
        print(f"Failed to instrument FastAPI with logfire: {e}")
        return False


def initialize_logfire(app: Optional[FastAPI] = None) -> Dict[str, Any]:
    """
    Complete logfire initialization including configuration and instrumentation.
    
    Args:
        app: Optional FastAPI application instance for instrumentation
        
    Returns:
        dict: Initialization results with status for each component
    """
    results = {
        "configured": False,
        "instrumentation": {
            "pydantic_ai": False,
            "redis": False,
            "httpx": False,
            "fastapi": False
        }
    }
    
    # Set up basic logfire configuration
    results["configured"] = setup_logfire()
    
    if results["configured"]:
        # Set up library instrumentation
        instrumentation_results = instrument_logfire()
        results["instrumentation"].update(instrumentation_results)
        
        # Set up FastAPI instrumentation if app is provided
        if app is not None:
            results["instrumentation"]["fastapi"] = instrument_fastapi(app)
    
    return results


def is_logfire_enabled() -> bool:
    """
    Check if logfire is enabled in settings.
    
    Returns:
        bool: True if logfire is enabled, False otherwise
    """
    return settings.logfire__enabled


def get_logfire_service_name() -> str:
    """
    Get the configured logfire service name.
    
    Returns:
        str: The logfire service name
    """
    return settings.logfire__service_name


def get_logfire_environment() -> str:
    """
    Get the configured logfire environment.
    
    Returns:
        str: The logfire environment
    """
    return settings.logfire__environment 