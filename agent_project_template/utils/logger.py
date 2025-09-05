"""
Logger Utility

Simplified logging configuration for AI Agents project with Logfire integration.
Based on official Logfire documentation best practices.
"""

import logging
import logging.config
import sys
from typing import Dict, Any, Optional
from pathlib import Path
from functools import lru_cache
from contextvars import ContextVar

from ai_agents.core.config import settings

# Context variable to store session ID for logging
_session_id_context: ContextVar[Optional[str]] = ContextVar('session_id', default=None)


def set_session_id(session_id: str) -> None:
    """Set the session ID in the current context for logging."""
    _session_id_context.set(session_id)


def get_session_id() -> Optional[str]:
    """Get the current session ID from context."""
    return _session_id_context.get()


def clear_session_id() -> None:
    """Clear the session ID from the current context."""
    _session_id_context.set(None)


def get_logfire_with_session():
    """
    Get a logfire instance with session ID as tag if available.

    Returns:
        Logfire instance with session tag if session exists,
        default logfire instance if no session,
        or None if logfire not available
    """
    try:
        import logfire

        session_id = get_session_id()
        if session_id:
            # Only create logfire instance with session tag if session ID exists
            return logfire.with_tags(f"sid:{session_id}")
        else:
            # Return default logfire instance without any session tags
            return logfire

    except ImportError:
        return None


class SessionAwareLogfireHandler(logging.Handler):
    """
    Custom Logfire handler that automatically adds session ID as tag.
    """

    def __init__(self, level=logging.NOTSET, fallback=None, logfire_instance=None):
        super().__init__(level=level)
        self.fallback = fallback or logging.StreamHandler(sys.stderr)
        self.logfire_instance = logfire_instance

    def emit(self, record):
        """Send the log to Logfire with session tag if available."""
        try:
            import logfire

            # Check if instrumentation is suppressed (simplified check)
            try:
                from opentelemetry.context import get_current
                from opentelemetry.instrumentation.utils import _SUPPRESS_INSTRUMENTATION_KEY
                if get_current().get(_SUPPRESS_INSTRUMENTATION_KEY):
                    self.fallback.handle(record)
                    return
            except ImportError:
                # If OpenTelemetry is not available, continue with logging
                pass

        except ImportError:
            self.fallback.handle(record)
            return
        except Exception:
            # If we can't check suppression, continue with logging
            pass

        try:
            # Get session ID and create appropriate logfire instance
            session_id = get_session_id()
            if session_id:
                # Only create logfire instance with session tag if session ID exists
                logfire_with_session = logfire.with_tags(f"sid:{session_id}")
            else:
                # Use default logfire instance without any session tags
                logfire_with_session = self.logfire_instance or logfire

            # Prepare attributes from log record
            attributes = {k: v for k, v in record.__dict__.items()
                         if k not in ['name', 'msg', 'args', 'levelname', 'levelno',
                                    'pathname', 'filename', 'module', 'lineno', 'funcName',
                                    'created', 'msecs', 'relativeCreated', 'thread',
                                    'threadName', 'processName', 'process', 'getMessage',
                                    'exc_info', 'exc_text', 'stack_info']}

            # Add code location attributes
            attributes['code.filepath'] = record.pathname
            attributes['code.lineno'] = record.lineno
            attributes['code.function'] = record.funcName

            # Format the message
            try:
                msg = record.getMessage()
            except Exception:
                msg = str(record.msg)

            # Send to logfire
            logfire_with_session.log(
                level=record.levelname.lower(),
                msg_template=msg,
                attributes=attributes,
                exc_info=record.exc_info
            )

        except Exception as e:
            # Fallback to standard handler if logfire fails
            self.fallback.handle(record)


def get_logging_config() -> Dict[str, Any]:
    """
    Generate logging configuration with Logfire integration.
    
    Returns:
        Dict: Complete logging configuration dictionary
    """
    
    # Determine log level
    log_level = settings.log_level.upper()
    
    # Create logs directory for fallback
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Base handlers - always include console and file for fallback
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "simple",
            "stream": sys.stdout
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": str(logs_dir / "ai_agents.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 3,
            "encoding": "utf-8"
        }
    }
    
    # Configure Logfire handler if enabled
    # Note: This will be added after logfire.configure() is called in main.py
    if settings.logfire__enabled:
        # We'll add the logfire handler dynamically after configuration
        pass
    
    # Base configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": handlers,
        "loggers": {
            # AI Agents application loggers
            "ai_agents": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            # Third-party library loggers - reduce verbosity
            "uvicorn.access": {
                "level": "WARNING",
                "handlers": [],
                "propagate": False
            },
            "httpx": {
                "level": "WARNING",
                "handlers": [],
                "propagate": False
            },
            "urllib3": {
                "level": "WARNING",
                "handlers": [],
                "propagate": False
            }
        },
        "root": {
            "level": "WARNING",
            "handlers": ["console"]
        }
    }
    
    # Environment-specific adjustments
    if settings.environment == "production":
        config["loggers"]["ai_agents"]["level"] = "INFO"
        config["handlers"]["console"]["level"] = "WARNING"
        
    elif settings.environment == "development":
        config["loggers"]["ai_agents"]["level"] = "DEBUG"
        config["handlers"]["console"]["level"] = "DEBUG"
        
    elif settings.environment == "test":
        config["loggers"]["ai_agents"]["level"] = "WARNING"
        config["handlers"]["console"]["level"] = "ERROR"
    
    return config


def setup_logfire_handler():
    """
    Set up Logfire handler after logfire.configure() has been called.
    This should be called from main.py after Logfire is configured.
    """

    if not settings.logfire__enabled:
        return

    try:
        import logfire

        # Create fallback handler with urllib3 filtering
        fallback_handler = logging.StreamHandler(sys.stderr)
        fallback_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

        # Filter out urllib3 debug logs from fallback handler
        urllib3_filter = logging.Filter('urllib3')
        fallback_handler.addFilter(lambda record: not urllib3_filter.filter(record))

        # Create our custom session-aware Logfire handler
        logfire_handler = SessionAwareLogfireHandler(
            level=settings.log_level.upper(),
            fallback=fallback_handler,
            logfire_instance=logfire
        )

        # Get ai_agents logger and add Logfire handler
        ai_agents_logger = logging.getLogger("ai_agents")
        ai_agents_logger.addHandler(logfire_handler)

        # Update root logger to use Logfire
        root_logger = logging.getLogger()
        root_logger.handlers = [h for h in root_logger.handlers if not isinstance(h, logging.StreamHandler)]
        root_logger.addHandler(logfire_handler)

        # Log successful Logfire integration
        logger = logging.getLogger("ai_agents.logfire")
        logger.info("Session-aware Logfire logging handler configured successfully")

    except ImportError:
        logger = logging.getLogger("ai_agents.logfire")
        logger.warning("Logfire not available, using standard logging only")
    except Exception as e:
        logger = logging.getLogger("ai_agents.logfire")
        logger.error("Failed to configure Logfire handler: %s", str(e))


@lru_cache(maxsize=1)
def setup_logging() -> None:
    """
    Set up logging configuration for the entire application.
    This function should be called once during application startup.
    """
    
    config = get_logging_config()
    logging.config.dictConfig(config)
    
    # Log startup information
    logger = logging.getLogger("ai_agents.startup")
    logger.info(
        "Logging system initialized - Environment: %s, Level: %s, Logfire: %s",
        settings.environment,
        settings.log_level,
        settings.logfire__enabled
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name, typically __name__ of the calling module

    Returns:
        Logger: Configured logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("This is an info message")
    """

    # Ensure logging is set up
    setup_logging()

    # Get logger with ai_agents prefix if not already present
    if not name.startswith("ai_agents"):
        name = f"ai_agents.{name}"

    return logging.getLogger(name)





# Convenience function for backward compatibility
def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Set up and configure a logger (backward compatibility).
    
    Args:
        name: Logger name (optional)
        
    Returns:
        Logger: Configured logger instance
    """
    
    if name is None:
        name = "ai_agents.default"
        
    return get_logger(name) 