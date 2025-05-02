from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
import time

# Import routers
from .routers import acronyms, conversational, health, metrics
from .middleware import (
    rate_limit_middleware,
    validate_response_middleware,
    version_middleware
)
from .routers.metrics import collect_metrics
from .monitoring import aeo_metrics
from .sponsors import router as sponsors_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='searchbot_access.log'
)
logger = logging.getLogger('searchbot_monitor')

app = FastAPI(
    title="AcronymMeaning API",
    description="API for retrieving structured acronym definitions with sponsorship information",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.middleware("http")(version_middleware)
app.middleware("http")(validate_response_middleware)
app.middleware("http")(collect_metrics)

# Include routers
app.include_router(acronyms.router, prefix="/api/acronym", tags=["acronyms"])
app.include_router(conversational.router, prefix="/api/conversational", tags=["conversational"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(metrics.router, prefix="/api", tags=["metrics"])
app.include_router(aeo_metrics.router, prefix="/aeo", tags=["aeo"])
app.include_router(sponsors_router, prefix="/api", tags=["sponsors"])

# Middleware for logging
@app.middleware("http")
async def log_searchbot_access(request, call_next):
    user_agent = request.headers.get("user-agent", "")
    if "OpenAI-User" in user_agent:
        logger.info(f"SearchBot access: {request.method} {request.url.path} - {datetime.now()}")
    response = await call_next(request)
    return response

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log requests and track AEO metrics"""
    start_time = time.time()
    
    # Log OpenAI SearchBot requests
    user_agent = request.headers.get("user-agent", "").lower()
    if "openai" in user_agent or "chatgpt" in user_agent:
        logger.info(f"OpenAI SearchBot request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Calculate response time
    process_time = time.time() - start_time
    
    # Log AEO metrics for relevant endpoints
    if request.url.path.startswith("/api/conversational"):
        try:
            # Extract query parameters
            query = request.query_params.get("query", "")
            acronym = request.url.path.split("/")[-1]
            
            # Log AEO query
            aeo_metrics.log_aeo_query(
                query=query,
                source=user_agent,
                response_type="conversational",
                confidence=0.9,  # Default confidence
                context_relevance=0.9  # Default context relevance
            )
        except Exception as e:
            logger.error(f"Error logging AEO metrics: {e}")
    
    # Add response time to headers
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to AcronymMeaning API",
        "version": "1.0.0",
        "documentation": "/docs"
    } 