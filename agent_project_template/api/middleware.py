"""
FastAPI Middleware

Simple middleware for request logging.
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from ai_agents.utils.logger import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Simple middleware to log API requests and responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log basic information.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/handler in chain
            
        Returns:
            Response: HTTP response
        """
        
        start_time = time.time()
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request start (debug level)
        logger.debug("Request: %s %s from %s", method, path, client_ip)
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log request completion
            if response.status_code >= 500:
                logger.error("%s %s - %d (%.3fs)", method, path, response.status_code, duration)
            elif response.status_code >= 400:
                logger.warning("%s %s - %d (%.3fs)", method, path, response.status_code, duration)
            else:
                logger.info("%s %s - %d (%.3fs)", method, path, response.status_code, duration)
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error("Request failed: %s %s - %s (%.3fs)", method, path, str(e), duration, exc_info=True)
            raise 