from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Callable
import time
from functools import wraps
import json
from datetime import datetime, timedelta

# Rate limiting configuration
RATE_LIMIT = 100  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

# In-memory rate limiting (replace with Redis in production)
request_counts = {}

def rate_limit_middleware():
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host
            current_time = datetime.now()
            
            # Clean up old entries
            for ip, (count, timestamp) in list(request_counts.items()):
                if current_time - timestamp > timedelta(seconds=RATE_LIMIT_WINDOW):
                    del request_counts[ip]
            
            # Check rate limit
            if client_ip in request_counts:
                count, timestamp = request_counts[client_ip]
                if count >= RATE_LIMIT:
                    if current_time - timestamp < timedelta(seconds=RATE_LIMIT_WINDOW):
                        raise HTTPException(
                            status_code=429,
                            detail="Too many requests. Please try again later."
                        )
                    else:
                        request_counts[client_ip] = (1, current_time)
                else:
                    request_counts[client_ip] = (count + 1, timestamp)
            else:
                request_counts[client_ip] = (1, current_time)
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

# Response validation middleware
async def validate_response_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    # Add response time header
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Validate response format
    if response.status_code == 200:
        try:
            content = json.loads(response.body.decode())
            if not isinstance(content, (dict, list)):
                raise HTTPException(
                    status_code=500,
                    detail="Invalid response format"
                )
        except:
            pass
    
    return response

# API versioning middleware
async def version_middleware(request: Request, call_next):
    version = request.headers.get("X-API-Version", "1.0")
    response = await call_next(request)
    response.headers["X-API-Version"] = version
    return response 