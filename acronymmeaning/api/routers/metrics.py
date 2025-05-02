from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Dict, List
import time
from datetime import datetime, timedelta

router = APIRouter()

# In-memory metrics storage (replace with proper database in production)
metrics_data = {
    "requests": [],
    "errors": [],
    "response_times": []
}

class MetricsResponse(BaseModel):
    total_requests: int
    error_rate: float
    average_response_time: float
    requests_by_endpoint: Dict[str, int]
    recent_errors: List[Dict]

@router.get("/metrics")
async def get_metrics():
    """
    Get API metrics and performance statistics
    """
    current_time = datetime.now()
    one_hour_ago = current_time - timedelta(hours=1)
    
    # Filter recent data
    recent_requests = [r for r in metrics_data["requests"] if r["timestamp"] > one_hour_ago]
    recent_errors = [e for e in metrics_data["errors"] if e["timestamp"] > one_hour_ago]
    recent_times = [t for t in metrics_data["response_times"] if t["timestamp"] > one_hour_ago]
    
    # Calculate metrics
    total_requests = len(recent_requests)
    error_rate = len(recent_errors) / total_requests if total_requests > 0 else 0
    avg_response_time = sum(t["time"] for t in recent_times) / len(recent_times) if recent_times else 0
    
    # Count requests by endpoint
    endpoint_counts = {}
    for request in recent_requests:
        endpoint = request["endpoint"]
        endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1
    
    return MetricsResponse(
        total_requests=total_requests,
        error_rate=error_rate,
        average_response_time=avg_response_time,
        requests_by_endpoint=endpoint_counts,
        recent_errors=recent_errors
    )

# Middleware to collect metrics
async def collect_metrics(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Record metrics
        metrics_data["requests"].append({
            "timestamp": datetime.now(),
            "endpoint": request.url.path,
            "method": request.method,
            "status_code": response.status_code
        })
        
        metrics_data["response_times"].append({
            "timestamp": datetime.now(),
            "endpoint": request.url.path,
            "time": process_time
        })
        
        if response.status_code >= 400:
            metrics_data["errors"].append({
                "timestamp": datetime.now(),
                "endpoint": request.url.path,
                "status_code": response.status_code,
                "error": response.body.decode() if hasattr(response, 'body') else None
            })
        
        return response
    except Exception as e:
        metrics_data["errors"].append({
            "timestamp": datetime.now(),
            "endpoint": request.url.path,
            "error": str(e)
        })
        raise 