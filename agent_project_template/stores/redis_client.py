"""
Redis Client Manager

Redis connection management and basic operations for AI Agents project.
"""

import asyncio
import json
import logging
from typing import Optional, Any, Dict, List, Union
from contextlib import asynccontextmanager
import redis.asyncio as redis
from redis.asyncio import ConnectionPool
from ai_agents.core.config import settings
from ai_agents.core.exceptions import InternalServiceException
from ai_agents.core.error_codes import InternalServiceErrorCode
import time

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Redis client wrapper with connection pooling and common operations.
    """
    
    def __init__(self):
        """Initialize Redis client with connection pool."""
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._lock = asyncio.Lock()
    
    async def _ensure_connection(self) -> redis.Redis:
        """
        Ensure Redis connection is established.
        
        Returns:
            redis.Redis: Redis client instance
            
        Raises:
            InternalServiceException: If connection fails
        """
        if self._client is not None:
            return self._client
            
        async with self._lock:
            if self._client is not None:
                return self._client
                
            try:
                # Build Redis connection URL from settings
                scheme = "rediss" if settings.redis__ssl else "redis"
                auth = f":{settings.redis__password}@" if settings.redis__password else ""
                redis_url = f"{scheme}://{auth}{settings.redis__host}:{settings.redis__port}/{settings.redis__db}"
                
                # Create connection pool with advanced settings
                pool_kwargs = {
                    "encoding": "utf-8",
                    "decode_responses": True,
                    "max_connections": settings.redis__pool_max_connections,
                    "retry_on_timeout": True,
                    "socket_connect_timeout": settings.redis__connect_timeout / 1000.0,  # Convert ms to seconds
                    "socket_timeout": settings.redis__socket_timeout / 1000.0,  # Convert ms to seconds
                }
                
                # Add SSL configuration if enabled
                if settings.redis__ssl:
                    pool_kwargs["connection_class"] = redis.SSLConnection
                    pool_kwargs["ssl_check_hostname"] = False
                    pool_kwargs["ssl_cert_reqs"] = None
                
                self._pool = ConnectionPool.from_url(redis_url, **pool_kwargs)
                
                # Create Redis client
                self._client = redis.Redis(connection_pool=self._pool)
                
                # Test connection
                await self._client.ping()
                logger.info("Redis connection established successfully")
                
                return self._client
                
            except Exception as e:
                logger.error("Failed to connect to Redis: %s", str(e))
                raise InternalServiceException(
                    InternalServiceErrorCode.SERVICE_INIT_FAILED,
                    detail=f"Redis connection failed: {str(e)}"
                )
    
    async def close(self):
        """Close Redis connection and cleanup resources."""
        if self._client:
            await self._client.aclose()
            self._client = None
        if self._pool:
            await self._pool.aclose()
            self._pool = None
        logger.info("Redis connection closed")
    
    # Basic Key-Value Operations
    async def get(self, key: str) -> Optional[str]:
        """
        Get value by key.
        
        Args:
            key: Redis key
            
        Returns:
            Value or None if key doesn't exist
        """
        client = await self._ensure_connection()
        return await client.get(key)
    
    async def set(
        self, 
        key: str, 
        value: str, 
        ex: Optional[int] = None,
        nx: bool = False
    ) -> bool:
        """
        Set key-value pair.
        
        Args:
            key: Redis key
            value: Value to set
            ex: Expiration time in seconds
            nx: Only set if key doesn't exist
            
        Returns:
            True if successful, False otherwise
        """
        client = await self._ensure_connection()
        return await client.set(key, value, ex=ex, nx=nx)
    
    async def delete(self, *keys: str) -> int:
        """
        Delete keys.
        
        Args:
            keys: Keys to delete
            
        Returns:
            Number of keys deleted
        """
        client = await self._ensure_connection()
        return await client.delete(*keys)
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists.
        
        Args:
            key: Redis key
            
        Returns:
            True if key exists, False otherwise
        """
        client = await self._ensure_connection()
        return bool(await client.exists(key))
    
    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration time for key.
        
        Args:
            key: Redis key
            seconds: Expiration time in seconds
            
        Returns:
            True if successful, False otherwise
        """
        client = await self._ensure_connection()
        return await client.expire(key, seconds)
    
    # JSON Operations
    async def set_json(
        self, 
        key: str, 
        data: Any, 
        ex: Optional[int] = None
    ) -> bool:
        """
        Set JSON data.
        
        Args:
            key: Redis key
            data: Data to serialize and store
            ex: Expiration time in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            return await self.set(key, json_str, ex=ex)
        except (TypeError, ValueError) as e:
            logger.error("Failed to serialize data for key %s: %s", key, str(e))
            return False
    
    async def get_json(self, key: str) -> Optional[Any]:
        """
        Get JSON data.
        
        Args:
            key: Redis key
            
        Returns:
            Deserialized data or None if key doesn't exist
        """
        json_str = await self.get(key)
        if json_str is None:
            return None
        
        try:
            return json.loads(json_str)
        except (TypeError, ValueError) as e:
            logger.error("Failed to deserialize data for key %s: %s", key, str(e))
            return None
    
    # Hash Operations
    async def hset(self, name: str, mapping: Dict[str, str]) -> int:
        """
        Set hash fields.
        
        Args:
            name: Hash name
            mapping: Field-value mapping
            
        Returns:
            Number of fields set
        """
        client = await self._ensure_connection()
        return await client.hset(name, mapping=mapping)
    
    async def hget(self, name: str, key: str) -> Optional[str]:
        """
        Get hash field value.
        
        Args:
            name: Hash name
            key: Field name
            
        Returns:
            Field value or None
        """
        client = await self._ensure_connection()
        return await client.hget(name, key)
    
    async def hgetall(self, name: str) -> Dict[str, str]:
        """
        Get all hash fields and values.
        
        Args:
            name: Hash name
            
        Returns:
            Dictionary of field-value pairs
        """
        client = await self._ensure_connection()
        return await client.hgetall(name)
    
    async def hdel(self, name: str, *keys: str) -> int:
        """
        Delete hash fields.
        
        Args:
            name: Hash name
            keys: Field names to delete
            
        Returns:
            Number of fields deleted
        """
        client = await self._ensure_connection()
        return await client.hdel(name, *keys)
    
    # List Operations
    async def lpush(self, name: str, *values: str) -> int:
        """
        Push values to the left of list.
        
        Args:
            name: List name
            values: Values to push
            
        Returns:
            List length after push
        """
        client = await self._ensure_connection()
        return await client.lpush(name, *values)
    
    async def rpush(self, name: str, *values: str) -> int:
        """
        Push values to the right of list.
        
        Args:
            name: List name
            values: Values to push
            
        Returns:
            List length after push
        """
        client = await self._ensure_connection()
        return await client.rpush(name, *values)
    
    async def lpop(self, name: str) -> Optional[str]:
        """
        Pop value from the left of list.
        
        Args:
            name: List name
            
        Returns:
            Popped value or None
        """
        client = await self._ensure_connection()
        return await client.lpop(name)
    
    async def rpop(self, name: str) -> Optional[str]:
        """
        Pop value from the right of list.
        
        Args:
            name: List name
            
        Returns:
            Popped value or None
        """
        client = await self._ensure_connection()
        return await client.rpop(name)
    
    async def lrange(self, name: str, start: int = 0, end: int = -1) -> List[str]:
        """
        Get list range.
        
        Args:
            name: List name
            start: Start index
            end: End index (-1 for end of list)
            
        Returns:
            List of values
        """
        client = await self._ensure_connection()
        return await client.lrange(name, start, end)
    
    # Distributed Lock Operations
    async def acquire_lock(
        self, 
        lock_key: str, 
        timeout: int = 30,
        identifier: Optional[str] = None
    ) -> Optional[str]:
        """
        Acquire distributed lock.
        
        Args:
            lock_key: Lock key
            timeout: Lock timeout in seconds
            identifier: Lock identifier (auto-generated if None)
            
        Returns:
            Lock identifier if acquired, None otherwise
        """
        import uuid
        import time
        
        if identifier is None:
            identifier = str(uuid.uuid4())
        
        client = await self._ensure_connection()
        
        # Try to acquire lock with expiration
        acquired = await client.set(lock_key, identifier, nx=True, ex=timeout)
        
        if acquired:
            logger.debug("Lock acquired: %s with identifier: %s", lock_key, identifier)
            return identifier
        else:
            logger.debug("Failed to acquire lock: %s", lock_key)
            return None
    
    async def release_lock(self, lock_key: str, identifier: str) -> bool:
        """
        Release distributed lock.
        
        Args:
            lock_key: Lock key
            identifier: Lock identifier
            
        Returns:
            True if lock was released, False otherwise
        """
        client = await self._ensure_connection()
        
        # Lua script to ensure atomic check-and-delete
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        try:
            result = await client.eval(lua_script, 1, lock_key, identifier)
            if result:
                logger.debug("Lock released: %s with identifier: %s", lock_key, identifier)
                return True
            else:
                logger.warning("Lock release failed: %s with identifier: %s", lock_key, identifier)
                return False
        except Exception as e:
            logger.error("Error releasing lock %s: %s", lock_key, str(e))
            return False
    
    @asynccontextmanager
    async def lock(
        self, 
        lock_key: str, 
        timeout: int = 30,
        wait_timeout: int = 10
    ):
        """
        Context manager for distributed lock.
        
        Args:
            lock_key: Lock key
            timeout: Lock timeout in seconds
            wait_timeout: Maximum time to wait for lock acquisition
            
        Yields:
            Lock identifier if acquired
            
        Raises:
            InternalServiceException: If lock cannot be acquired
        """
        import asyncio
        import time
        
        start_time = time.time()
        identifier = None
        
        # Try to acquire lock with retries
        while time.time() - start_time < wait_timeout:
            identifier = await self.acquire_lock(lock_key, timeout)
            if identifier:
                break
            await asyncio.sleep(0.1)
        
        if not identifier:
            raise InternalServiceException(
                InternalServiceErrorCode.SERVICE_INIT_FAILED,
                detail=f"Failed to acquire lock {lock_key} within {wait_timeout} seconds"
            )
        
        try:
            yield identifier
        finally:
            await self.release_lock(lock_key, identifier)
    
    # Health Check
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform Redis health check.
        
        Returns:
            Health check result
        """
        try:
            client = await self._ensure_connection()
            
            # Test basic operations
            start_time = time.time()
            await client.ping()
            ping_time = time.time() - start_time
            
            # Get Redis info
            info = await client.info('server')
            
            # Get connection pool info
            pool_info = {}
            if self._pool:
                try:
                    pool_info = {
                        "max_connections": getattr(self._pool, 'max_connections', 'N/A'),
                        "created_connections": getattr(self._pool, 'created_connections', 'N/A'),
                        "available_connections": len(getattr(self._pool, '_available_connections', [])),
                        "in_use_connections": len(getattr(self._pool, '_in_use_connections', []))
                    }
                except Exception as e:
                    pool_info = {"error": f"Failed to get pool info: {str(e)}"}
            
            return {
                "status": "healthy",
                "ping_time_ms": round(ping_time * 1000, 2),
                "redis_version": info.get('redis_version'),
                "connected_clients": info.get('connected_clients'),
                "used_memory_human": info.get('used_memory_human'),
                "uptime_in_seconds": info.get('uptime_in_seconds'),
                "connection_pool": pool_info,
                "config": {
                    "ssl_enabled": settings.redis__ssl,
                    "database": settings.redis__db,
                    "host": settings.redis__host,
                    "port": settings.redis__port,
                    "connect_timeout_ms": settings.redis__connect_timeout,
                    "socket_timeout_ms": settings.redis__socket_timeout,
                    "pool_max_connections": settings.redis__pool_max_connections,
                    "pool_max_idle": settings.redis__pool_max_idle,
                    "pool_min_idle": settings.redis__pool_min_idle,
                    "pool_max_wait": settings.redis__pool_max_wait
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """
    Get global Redis client instance.
    
    Returns:
        RedisClient: Global Redis client instance
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client


async def close_redis_client():
    """Close global Redis client."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None 