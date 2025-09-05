"""
Snowflake ID Generator Utility

Provides distributed unique ID generation using SonyFlake algorithm.
Implements singleton pattern for consistent machine ID across the application.
"""

import threading
from typing import Optional
from sonyflake import SonyFlake
from ai_agents.utils.logger import get_logger
from ai_agents.core.exceptions import InternalServiceException
from ai_agents.core.error_codes import InternalServiceErrorCode

logger = get_logger(__name__)


class SnowflakeGenerator:
    """
    Singleton Snowflake ID generator using SonyFlake algorithm.
    
    SonyFlake generates IDs with the following structure:
    - 39 bits for time in units of 10 msec
    - 8 bits for a sequence number  
    - 16 bits for a machine id
    
    This ensures distributed uniqueness and time-based ordering.
    """
    
    _instance: Optional['SnowflakeGenerator'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'SnowflakeGenerator':
        """Singleton pattern implementation with thread safety."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the SonyFlake generator (called only once due to singleton)."""
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        try:
            # Initialize SonyFlake with default configuration
            # machine_id will be automatically determined
            self._sf = SonyFlake()
            self._initialized = True
            logger.info("SnowflakeGenerator initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize SnowflakeGenerator: %s", str(e))
            raise
    
    def generate_id(self) -> int:
        """
        Generate a unique snowflake ID.
        
        Returns:
            int: Unique distributed ID as integer
            
        Raises:
            InternalServiceException: If ID generation fails
        """
        try:
            return self._sf.next_id()
        except Exception as e:
            logger.error("Failed to generate snowflake ID: %s", str(e))
            raise InternalServiceException(
                InternalServiceErrorCode.SERVICE_UNAVAILABLE,
                f"Snowflake ID generation failed: {str(e)}"
            )
    
    def generate_id_str(self) -> str:
        """
        Generate a unique snowflake ID as string.
        
        Returns:
            str: Unique distributed ID as string
            
        Raises:
            RuntimeError: If ID generation fails
        """
        return str(self.generate_id())


# Global singleton instance
_generator: Optional[SnowflakeGenerator] = None


def get_snowflake_generator() -> SnowflakeGenerator:
    """
    Get the global SnowflakeGenerator singleton instance.
    
    Returns:
        SnowflakeGenerator: The singleton generator instance
    """
    global _generator
    if _generator is None:
        _generator = SnowflakeGenerator()
    return _generator


def generate_snowflake_id() -> int:
    """
    Convenience function to generate a snowflake ID.
    
    Returns:
        int: Unique distributed ID as integer
    """
    return get_snowflake_generator().generate_id()


def generate_snowflake_id_str() -> str:
    """
    Convenience function to generate a snowflake ID as string.
    
    Returns:
        str: Unique distributed ID as string
    """
    return get_snowflake_generator().generate_id_str() 