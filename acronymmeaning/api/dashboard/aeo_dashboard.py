from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, List
import json
from datetime import datetime, timedelta
from api.monitoring.aeo_metrics import get_aeo_analytics

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def format_metrics_for_dashboard(metrics: Dict) -> Dict:
    """Format metrics for dashboard display"""
    return {
        "summary": {
            "total_queries": metrics["total_queries"],
            "unique_queries": metrics["unique_queries"],
            "average_confidence": f"{metrics['average_confidence']:.2%}",
            "average_context_relevance": f"{metrics['average_context_relevance']:.2%}"
        },
        "top_queries": [
            {"query": q["query"], "count": q["count"]}
            for q in metrics["top_queries"][:10]
        ],
        "query_patterns": [
            {"pattern": p, "count": c}
            for p, c in sorted(metrics["query_patterns"].items(), key=lambda x: x[1], reverse=True)[:10]
        ],
        "response_types": [
            {"type": t, "count": c}
            for t, c in sorted(metrics["response_types"].items(), key=lambda x: x[1], reverse=True)
        ]
    }

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, hours: int = 24):
    """Render the AEO dashboard"""
    metrics = get_aeo_analytics(hours)
    formatted_metrics = format_metrics_for_dashboard(metrics)
    
    return templates.TemplateResponse(
        "aeo_dashboard.html",
        {
            "request": request,
            "metrics": formatted_metrics,
            "time_period": hours
        }
    )

@router.get("/data")
async def dashboard_data(hours: int = 24):
    """Get dashboard data in JSON format"""
    metrics = get_aeo_analytics(hours)
    return format_metrics_for_dashboard(metrics) 