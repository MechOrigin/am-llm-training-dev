from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import os
from datetime import datetime, timedelta
import logging

router = APIRouter()

class AEOQuery(BaseModel):
    query: str
    timestamp: datetime
    source: str
    response_type: str
    confidence: float
    context_relevance: float

class TopQuery(BaseModel):
    query: str
    count: int

class AEOAnalytics(BaseModel):
    total_queries: int
    unique_queries: int
    average_confidence: float
    average_context_relevance: float
    top_queries: List[TopQuery]
    query_patterns: Dict[str, int]
    response_types: Dict[str, int]

# In-memory storage for AEO metrics
aeo_queries: List[AEOQuery] = []
query_patterns: Dict[str, int] = {}
response_types: Dict[str, int] = {}

def log_aeo_query(query: str, source: str, response_type: str, confidence: float, context_relevance: float):
    """Log an AEO query and its performance metrics"""
    query_data = AEOQuery(
        query=query,
        timestamp=datetime.now(),
        source=source,
        response_type=response_type,
        confidence=confidence,
        context_relevance=context_relevance
    )
    
    aeo_queries.append(query_data)
    
    # Update query patterns
    pattern = query.lower()
    query_patterns[pattern] = query_patterns.get(pattern, 0) + 1
    
    # Update response types
    response_types[response_type] = response_types.get(response_type, 0) + 1
    
    # Log the query
    logging.info(f"AEO Query: {query} | Source: {source} | Confidence: {confidence} | Context Relevance: {context_relevance}")

@router.post("/log")
async def log_aeo_query(query: AEOQuery):
    """Log a new AEO query"""
    aeo_queries.append(query)
    
    # Update query patterns
    pattern = query.query.lower()
    query_patterns[pattern] = query_patterns.get(pattern, 0) + 1
    
    # Update response types
    response_types[query.response_type] = response_types.get(query.response_type, 0) + 1
    
    return {"status": "success"}

def get_aeo_analytics(hours: int = 24) -> AEOAnalytics:
    """Get AEO analytics for the specified time period"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    recent_queries = [q for q in aeo_queries if q.timestamp >= cutoff_time]
    
    if not recent_queries:
        return AEOAnalytics(
            total_queries=0,
            unique_queries=0,
            average_confidence=0,
            average_context_relevance=0,
            top_queries=[],
            query_patterns={},
            response_types={}
        )
    
    # Calculate metrics
    total_queries = len(recent_queries)
    unique_queries = len(set(q.query for q in recent_queries))
    average_confidence = sum(q.confidence for q in recent_queries) / total_queries
    average_context_relevance = sum(q.context_relevance for q in recent_queries) / total_queries
    
    # Get top queries
    query_counts = {}
    for q in recent_queries:
        query_counts[q.query] = query_counts.get(q.query, 0) + 1
    top_queries = [TopQuery(query=q, count=c) for q, c in sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
    
    return AEOAnalytics(
        total_queries=total_queries,
        unique_queries=unique_queries,
        average_confidence=average_confidence,
        average_context_relevance=average_context_relevance,
        top_queries=top_queries,
        query_patterns=query_patterns,
        response_types=response_types
    )

@router.get("/metrics")
async def get_metrics(hours: int = 24):
    """Get AEO metrics for the specified time period"""
    return get_aeo_analytics(hours) 