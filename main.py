"""
Application Entry Point
"""

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any
from ai_agents.core.config import settings
from ai_agents.api.router import router
from ai_agents.api.middleware import RequestLoggingMiddleware
from ai_agents.utils.logger import setup_logging, get_logger
from ai_agents.core.redis_client import get_redis_client, close_redis_client
from ai_agents.core.logfire_config import initialize_logfire
from ai_agents.core.database import test_connection, get_pool_status
from ai_agents.core.exception_handlers import global_exception_handler



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup operations
    print("AI Agents application starting up...")
    print(f"Environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")
    print(f"Log level: {settings.log_level}")
    
    if settings.logfire__enabled:
        print(f"Logfire monitoring enabled for service: {settings.logfire__service_name}")
    
    # Initialize PostgreSQL connection
    try:
        test_connection()
        print("PostgreSQL connection pool initialized successfully.")
    except Exception as e:
        print(f"PostgreSQL initialization failed: {str(e)}")
        raise
    
    # Initialize Redis connection
    try:
        redis_client = get_redis_client()
        # Test Redis connection
        health = await redis_client.health_check()
        if health["status"] == "healthy":
            print(f"Redis connection healthy - version: {health.get('redis_version', 'unknown')}")
        else:
            print(f"Redis connection warning: {health.get('error', 'unknown')}")
    except Exception as e:
        print(f"Redis initialization failed: {str(e)}")
    
    yield
    
    # Shutdown operations
    print("AI Agents application shutting down...")
    
    # Close Redis connection
    try:
        await close_redis_client()
        print("Redis connection closed")
    except Exception as e:
        print(f"Error closing Redis connection: {str(e)}")


def get_db_pool_status():
    """
    Get database connection pool status for monitoring.
    
    Returns:
        dict: Connection pool status information
    """
    return get_pool_status()


def _get_pool_recommendations(pool_status: Dict[str, Any]) -> list:
    """
    Generate recommendations based on connection pool status.
    
    Args:
        pool_status: Current pool status
        
    Returns:
        list: List of recommendations
    """
    recommendations = []
    
    checked_out = pool_status.get("checked_out", 0)
    pool_size_limit = pool_status.get("pool_size_limit", settings.database__pool_size)
    overflow = pool_status.get("overflow", 0)
    max_overflow = pool_status.get("max_overflow", settings.database__max_overflow)
    
    if isinstance(pool_size_limit, int) and checked_out >= pool_size_limit * 0.8:
        recommendations.append("Consider increasing pool_size or investigating connection leaks")
    
    if isinstance(max_overflow, int) and overflow >= max_overflow * 0.5:
        recommendations.append("Consider increasing max_overflow or optimizing connection usage")
    
    if not recommendations:
        recommendations.append("Connection pool is operating within normal parameters")
    
    return recommendations


def create_main_app() -> FastAPI:
    """
    Create and configure the main FastAPI application.
    
    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    # Initialize basic logging system first (without Logfire)
    setup_logging()
    
    # Initialize Logfire configuration first (without FastAPI instrumentation)
    from ai_agents.core.logfire_config import setup_logfire, instrument_logfire
    setup_logfire()
    instrument_logfire()
    
    # Now get logger after Logfire is configured
    logger = get_logger(__name__)
    logger.info("Starting AI Agents application initialization")
    
    app = FastAPI(
        title=settings.api__title,
        description=settings.api__description,
        version=settings.api__version,
        lifespan=lifespan,
        docs_url=settings.api__docs_url,
        redoc_url=settings.api__redoc_url
    )
    
    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins_list,
        allow_credentials=settings.cors__allow_credentials,
        allow_methods=settings.cors_allow_methods_list,
        allow_headers=settings.cors_allow_headers_list,
    )
    
    # Instrument FastAPI with logfire (after middleware setup but before routes)
    from ai_agents.core.logfire_config import instrument_fastapi
    instrument_fastapi(app)
    
    app.include_router(router)
    
    app.add_exception_handler(Exception, global_exception_handler)
    
    @app.get("/health", summary="系统健康检查", description="检查系统整体健康状态，包括数据库和Redis连接")
    async def health_check() -> Dict[str, Any]:
        """
        Comprehensive system health check endpoint
        
        Returns:
            Dict[str, Any]: Complete system health status including all components
        """
        health_status = {
            "status": "healthy",
            "message": "AI Agents service is running",
            "version": settings.api__version,
            "environment": settings.environment,
            "debug": settings.debug,
            "components": {}
        }
        
        # Check database connectivity
        try:
            test_connection()
            health_status["components"]["database"] = {
                "status": "healthy",
                "message": "Database connection successful"
            }
            logger.debug("Database health check passed")
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }
            logger.error("Database health check failed: %s", str(e))
        
        # Check Redis connectivity
        try:
            redis_client = get_redis_client()
            redis_health = await redis_client.health_check()
            health_status["components"]["redis"] = {
                "status": "healthy" if redis_health["status"] == "healthy" else "unhealthy",
                "message": "Redis connection successful" if redis_health["status"] == "healthy" else f"Redis connection failed: {redis_health.get('error', 'unknown')}"
            }
            logger.debug("Redis health check passed")
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["components"]["redis"] = {
                "status": "unhealthy",
                "message": f"Redis connection failed: {str(e)}"
            }
            logger.error("Redis health check failed: %s", str(e))
        
        # Add connection pool status
        try:
            pool_status = get_pool_status()
            health_status["components"]["connection_pool"] = {
                "status": "healthy",
                "details": pool_status
            }
            
            # Check for potential connection pool issues
            checked_out = pool_status.get("checked_out", 0)
            pool_size_limit = pool_status.get("pool_size_limit", settings.database__pool_size)
            
            if isinstance(pool_size_limit, int) and checked_out >= pool_size_limit * 0.8:
                health_status["components"]["connection_pool"]["status"] = "warning"
                health_status["components"]["connection_pool"]["message"] = f"High connection usage: {checked_out}/{pool_size_limit}"
                logger.warning("High database connection pool usage: %d/%d", checked_out, pool_size_limit)
                
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["components"]["connection_pool"] = {
                "status": "unhealthy",
                "message": f"Failed to get pool status: {str(e)}"
            }
            logger.error("Connection pool status check failed: %s", str(e))
        
        return health_status
    
    @app.get("/health/database", summary="数据库健康检查", description="详细的数据库健康检查，包括连接池状态")
    async def database_health_check(pool_status: dict = Depends(get_db_pool_status)) -> Dict[str, Any]:
        """
        Detailed database health check with connection pool monitoring.
        
        Args:
            pool_status: Connection pool status (injected)
            
        Returns:
            Dict[str, Any]: Detailed database health information
        """
        try:
            # Test database connection
            test_connection()
            
            # Analyze pool status
            checked_out = pool_status.get("checked_out", 0)
            pool_size = pool_status.get("size", 0)
            overflow = pool_status.get("overflow", 0)
            pool_size_limit = pool_status.get("pool_size_limit", settings.database__pool_size)
            max_overflow = pool_status.get("max_overflow", settings.database__max_overflow)
            
            # Determine health status based on pool metrics
            status = "healthy"
            warnings = []
            
            if isinstance(pool_size_limit, int):
                if checked_out >= pool_size_limit * 0.9:
                    status = "critical"
                    warnings.append(f"Critical: Connection pool nearly exhausted ({checked_out}/{pool_size_limit})")
                elif checked_out >= pool_size_limit * 0.8:
                    status = "warning"
                    warnings.append(f"Warning: High connection pool usage ({checked_out}/{pool_size_limit})")
            
            if isinstance(max_overflow, int) and overflow >= max_overflow * 0.8:
                status = "warning" if status == "healthy" else status
                warnings.append(f"Warning: High overflow usage ({overflow}/{max_overflow})")
            
            return {
                "status": status,
                "connection_test": "passed",
                "pool_status": pool_status,
                "warnings": warnings,
                "recommendations": _get_pool_recommendations(pool_status)
            }
            
        except Exception as e:
            logger.error("Database health check failed: %s", str(e))
            return {
                "status": "unhealthy",
                "connection_test": "failed",
                "error": str(e),
                "pool_status": pool_status
            }
    
    @app.get("/metrics/database", summary="数据库指标", description="获取数据库连接池详细指标，适用于监控系统")
    async def database_metrics(pool_status: dict = Depends(get_db_pool_status)) -> Dict[str, Any]:
        """
        Get database metrics in a format suitable for monitoring systems.
        
        Args:
            pool_status: Connection pool status (injected)
            
        Returns:
            Dict[str, Any]: Database metrics
        """
        return {
            "database_connections_active": pool_status.get("checked_out", 0),
            "database_connections_pool_size": pool_status.get("size", 0),
            "database_connections_overflow": pool_status.get("overflow", 0),
            "database_connections_pool_limit": pool_status.get("pool_size_limit", 0),
            "database_connections_max_overflow": pool_status.get("max_overflow", 0),
            "database_pool_utilization_percent": (
                (pool_status.get("checked_out", 0) / pool_status.get("pool_size_limit", 1)) * 100
                if isinstance(pool_status.get("pool_size_limit"), int) and pool_status.get("pool_size_limit", 0) > 0
                else 0
            )
        }
    
    @app.get("/")
    async def root():
        """
        Root path information
        
        Returns:
            dict: Application basic information
        """
        return {
            "name": settings.api__title,
            "description": settings.api__description,
            "version": settings.api__version,
            "docs_url": settings.api__docs_url,
            "redoc_url": settings.api__redoc_url,
            "health_check": "/health",
            "database_health": "/health/database",
            "database_metrics": "/metrics/database"
        }
    
    return app


# Create application instance only when accessed
def get_app():
    """Factory function to get the application instance"""
    return create_main_app()

# For deployment servers like gunicorn/uvicorn
app = get_app()


if __name__ == "__main__":
    """
    Entry point when running the file directly
    """
    import os
    
    # Get host and port from environment variables or use defaults
    # This allows Kubernetes/Zadig to override these values
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    
    print("Starting AI Agents in development mode...")
    print(f"Server will run on {host}:{port}")
    print(f"Environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")
    print(f"API docs: http://{host}:{port}{settings.api__docs_url}")
    
    uvicorn.run(
        "main:app",  # Use import string instead of function to allow reload
        host=host,
        port=port,
        reload=settings.debug,
        log_level=settings.log_level
    ) 