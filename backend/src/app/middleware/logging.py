import logging
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        if request.method in ["POST", "PUT"]:
            try:
                body = await request.json()
                logger.info(f"Request Body: {body}")
            except:
                pass

        # Get response
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: Status {response.status_code}, "
            f"Processed in {process_time:.3f} seconds"
        )
        
        return response 