"""
Redis Distributed Lock Utility

Session-level distributed lock implementation for AI Agents project.
Provides simple API for acquiring and releasing locks to prevent concurrent resume data modification.
"""

import asyncio
import logging
from typing import Optional
from contextlib import asynccontextmanager

from ai_agents.core.redis_client import get_redis_client
from ai_agents.core.exceptions import InternalServiceException
from ai_agents.core.error_codes import InternalServiceErrorCode
from ai_agents.core.config import settings
from ai_agents.utils.logger import get_logger

logger = get_logger(__name__)


class SessionLock:
    """
    Session-level distributed lock for resume data protection.
    
    This class provides a high-level interface for acquiring and releasing
    distributed locks using Redis, specifically designed for protecting
    resume data from concurrent modifications.
    """
    
    def __init__(self, session_id: str, timeout: int = 30):
        """
        Initialize session lock.

        Args:
            session_id: Session identifier
            timeout: Lock timeout in seconds (uses settings default if None)
        """
        self.session_id = session_id
        self.timeout = timeout
        self.lock_key = f"resume_lock:{session_id}"
        self._redis_client = get_redis_client()
        self._identifier: Optional[str] = None
    
    async def acquire(self, wait_timeout: int = 10) -> bool:
        """
        Acquire distributed lock for the session.
        
        Args:
            wait_timeout: Maximum time to wait for lock acquisition in seconds
            
        Returns:
            bool: True if lock acquired successfully, False otherwise
            
        Raises:
            InternalServiceException: If Redis operation fails
        """
        try:
            start_time = asyncio.get_event_loop().time()

            # Try to acquire lock with retries
            while (asyncio.get_event_loop().time() - start_time) < wait_timeout:
                self._identifier = await self._redis_client.acquire_lock(
                    self.lock_key, 
                    self.timeout
                )
                
                if self._identifier:
                    logger.info(
                        "Session lock acquired successfully for session: %s", 
                        self.session_id
                    )
                    return True
                
                # Wait before retry
                await asyncio.sleep(settings.redis_lock__retry_sleep_interval)
            
            logger.warning(
                "Failed to acquire session lock for session: %s within %d seconds", 
                self.session_id, 
                wait_timeout
            )
            return False
            
        except Exception as e:
            logger.error(
                "Error acquiring session lock for session: %s, error: %s", 
                self.session_id, 
                str(e)
            )
            raise InternalServiceException(
                InternalServiceErrorCode.SERVICE_UNAVAILABLE,
                detail=f"Failed to acquire session lock: {str(e)}"
            )
    
    async def release(self) -> bool:
        """
        Release distributed lock for the session.
        
        Returns:
            bool: True if lock released successfully, False otherwise
            
        Raises:
            InternalServiceException: If Redis operation fails
        """
        if not self._identifier:
            logger.warning(
                "Attempting to release lock without identifier for session: %s", 
                self.session_id
            )
            return False
        
        try:
            success = await self._redis_client.release_lock(
                self.lock_key, 
                self._identifier
            )
            
            if success:
                logger.info(
                    "Session lock released successfully for session: %s", 
                    self.session_id
                )
            else:
                logger.warning(
                    "Failed to release session lock for session: %s", 
                    self.session_id
                )
            
            self._identifier = None
            return success
            
        except Exception as e:
            logger.error(
                "Error releasing session lock for session: %s, error: %s", 
                self.session_id, 
                str(e)
            )
            raise InternalServiceException(
                InternalServiceErrorCode.SERVICE_UNAVAILABLE,
                detail=f"Failed to release session lock: {str(e)}"
            )
    
    @asynccontextmanager
    async def acquire_context(self, wait_timeout: int = 10):
        """
        Context manager for automatic lock acquisition and release.
        
        Args:
            wait_timeout: Maximum time to wait for lock acquisition in seconds
            
        Yields:
            bool: True if lock acquired successfully
            
        Raises:
            InternalServiceException: If lock cannot be acquired or Redis operation fails
            
        Example:
            async with SessionLock(session_id).acquire_context() as acquired:
                if acquired:
                    # Perform protected operations
                    pass
        """
        acquired = await self.acquire(wait_timeout)

        if not acquired:
            raise InternalServiceException(
                InternalServiceErrorCode.SERVICE_UNAVAILABLE,
                detail=f"Failed to acquire session lock for {self.session_id} within {wait_timeout} seconds"
            )
        
        try:
            yield acquired
        finally:
            await self.release()


# Convenience functions for backward compatibility with database design document
async def acquire_session_lock(session_id: str, timeout: int = 30) -> Optional[str]:
    """
    Acquire session-level distributed lock.
    
    Args:
        session_id: Session identifier
        timeout: Lock timeout in seconds
        
    Returns:
        Lock identifier if acquired, None otherwise
        
    Note:
        This function is provided for compatibility with the database design document.
        For new code, consider using SessionLock class for better error handling.
    """
    try:
        redis_client = get_redis_client()
        lock_key = f"resume_lock:{session_id}"
        identifier = await redis_client.acquire_lock(lock_key, timeout)
        
        if identifier:
            logger.info("Session lock acquired for session: %s", session_id)
        else:
            logger.warning("Failed to acquire session lock for session: %s", session_id)
            
        return identifier
        
    except Exception as e:
        logger.error(
            "Error acquiring session lock for session: %s, error: %s", 
            session_id, 
            str(e)
        )
        return None


async def release_session_lock(session_id: str, identifier: str) -> bool:
    """
    Release session-level distributed lock.
    
    Args:
        session_id: Session identifier
        identifier: Lock identifier returned by acquire_session_lock
        
    Returns:
        True if lock released successfully, False otherwise
        
    Note:
        This function is provided for compatibility with the database design document.
        For new code, consider using SessionLock class for better error handling.
    """
    try:
        redis_client = get_redis_client()
        lock_key = f"resume_lock:{session_id}"
        success = await redis_client.release_lock(lock_key, identifier)
        
        if success:
            logger.info("Session lock released for session: %s", session_id)
        else:
            logger.warning("Failed to release session lock for session: %s", session_id)
            
        return success
        
    except Exception as e:
        logger.error(
            "Error releasing session lock for session: %s, error: %s", 
            session_id, 
            str(e)
        )
        return False


# Context manager for session lock
@asynccontextmanager
async def session_lock_context(
    session_id: str,
    timeout: int = 30,
    wait_timeout: int = 10
):
    """
    Context manager for session-level distributed lock.
    
    Args:
        session_id: Session identifier
        timeout: Lock timeout in seconds
        wait_timeout: Maximum time to wait for lock acquisition
        
    Yields:
        str: Lock identifier if acquired
        
    Raises:
        InternalServiceException: If lock cannot be acquired
        
    Example:
        async with session_lock_context(session_id) as lock_id:
            # Perform protected operations
            pass
    """
    session_lock = SessionLock(session_id, timeout)

    async with session_lock.acquire_context(wait_timeout):
        yield session_lock._identifier