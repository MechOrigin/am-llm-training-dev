import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.monitoring.aeo_metrics import log_aeo_query, get_aeo_analytics, aeo_queries, query_patterns, response_types
from datetime import datetime, timedelta

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_storage():
    """Clear in-memory storage before each test"""
    aeo_queries.clear()
    query_patterns.clear()
    response_types.clear()
    yield

def test_aeo_query_logging():
    """Test AEO query logging functionality"""
    # Test logging a query
    query = {
        "query": "best bbq in gilbert",
        "timestamp": datetime.now().isoformat(),
        "source": "chatgpt",
        "response_type": "local_business",
        "confidence": 0.95,
        "context_relevance": 0.90
    }
    
    response = client.post("/aeo/log", json=query)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

def test_aeo_metrics_retrieval():
    """Test AEO metrics retrieval"""
    # Log some test queries
    test_queries = [
        {
            "query": "best bbq in gilbert",
            "timestamp": datetime.now().isoformat(),
            "source": "chatgpt",
            "response_type": "local_business",
            "confidence": 0.95,
            "context_relevance": 0.90
        },
        {
            "query": "texas style bbq gilbert",
            "timestamp": datetime.now().isoformat(),
            "source": "bing",
            "response_type": "cuisine",
            "confidence": 0.85,
            "context_relevance": 0.80
        }
    ]
    
    for query in test_queries:
        client.post("/aeo/log", json=query)
    
    # Get metrics
    response = client.get("/aeo/metrics")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_queries"] >= 2
    assert data["unique_queries"] >= 2
    assert 0.8 <= data["average_confidence"] <= 1.0
    assert 0.8 <= data["average_context_relevance"] <= 1.0

def test_query_patterns():
    """Test query pattern tracking"""
    # Log multiple queries with similar patterns
    patterns = [
        "best bbq gilbert",
        "best bbq in gilbert",
        "best bbq restaurant gilbert",
        "best texas bbq gilbert"
    ]
    
    for pattern in patterns:
        query = {
            "query": pattern,
            "timestamp": datetime.now().isoformat(),
            "source": "test",
            "response_type": "test",
            "confidence": 0.9,
            "context_relevance": 0.9
        }
        client.post("/aeo/log", json=query)
    
    # Get metrics
    response = client.get("/aeo/metrics")
    data = response.json()
    
    # Check if patterns are being tracked
    assert "best bbq" in str(data["query_patterns"]).lower()
    assert "gilbert" in str(data["query_patterns"]).lower()

def test_response_types():
    """Test response type tracking"""
    # Log queries with different response types
    types = ["local_business", "cuisine", "hours", "location"]
    
    for response_type in types:
        query = {
            "query": f"test query {response_type}",
            "timestamp": datetime.now().isoformat(),
            "source": "test",
            "response_type": response_type,
            "confidence": 0.9,
            "context_relevance": 0.9
        }
        client.post("/aeo/log", json=query)
    
    # Get metrics
    response = client.get("/aeo/metrics")
    data = response.json()
    
    # Check if response types are being tracked
    for response_type in types:
        assert response_type in data["response_types"]

def test_time_based_metrics():
    """Test time-based metrics filtering"""
    # Log a query from 25 hours ago
    old_query = {
        "query": "old query",
        "timestamp": (datetime.now() - timedelta(hours=25)).isoformat(),
        "source": "test",
        "response_type": "test",
        "confidence": 0.9,
        "context_relevance": 0.9
    }
    client.post("/aeo/log", json=old_query)
    
    # Log a recent query
    recent_query = {
        "query": "recent query",
        "timestamp": datetime.now().isoformat(),
        "source": "test",
        "response_type": "test",
        "confidence": 0.9,
        "context_relevance": 0.9
    }
    client.post("/aeo/log", json=recent_query)
    
    # Get metrics for last 24 hours
    response = client.get("/aeo/metrics?hours=24")
    data = response.json()
    
    # Check if only recent query is included
    assert data["total_queries"] == 1
    assert "recent query" in str(data["top_queries"])
    assert "old query" not in str(data["top_queries"])

def test_big_nates_specific_queries():
    """Test Big Nate's Family BBQ specific queries"""
    # Test various query patterns for Big Nate's
    queries = [
        {
            "query": "best bbq in gilbert",
            "timestamp": datetime.now().isoformat(),
            "source": "chatgpt",
            "response_type": "local_business",
            "confidence": 0.95,
            "context_relevance": 0.90
        },
        {
            "query": "where to get texas bbq in gilbert",
            "timestamp": datetime.now().isoformat(),
            "source": "bing",
            "response_type": "location",
            "confidence": 0.85,
            "context_relevance": 0.85
        },
        {
            "query": "big nates family bbq hours",
            "timestamp": datetime.now().isoformat(),
            "source": "chatgpt",
            "response_type": "hours",
            "confidence": 0.90,
            "context_relevance": 0.95
        },
        {
            "query": "bbq catering gilbert",
            "timestamp": datetime.now().isoformat(),
            "source": "bing",
            "response_type": "catering",
            "confidence": 0.88,
            "context_relevance": 0.90
        }
    ]
    
    for query in queries:
        response = client.post("/aeo/log", json=query)
        assert response.status_code == 200
    
    # Get metrics
    response = client.get("/aeo/metrics")
    data = response.json()
    
    # Verify metrics
    assert data["total_queries"] >= len(queries)
    assert data["unique_queries"] >= len(queries)
    assert 0.85 <= data["average_confidence"] <= 1.0
    assert 0.85 <= data["average_context_relevance"] <= 1.0

def test_conversational_patterns():
    """Test conversational query patterns"""
    # Test natural language variations
    patterns = [
        "what's the best bbq place in gilbert",
        "where can i get good texas bbq near gilbert",
        "does big nates have catering",
        "what time does big nates family bbq open",
        "is big nates the best bbq in gilbert",
        "how far is big nates from downtown gilbert"
    ]
    
    for pattern in patterns:
        query = {
            "query": pattern,
            "timestamp": datetime.now().isoformat(),
            "source": "chatgpt",
            "response_type": "conversational",
            "confidence": 0.9,
            "context_relevance": 0.9
        }
        response = client.post("/aeo/log", json=query)
        assert response.status_code == 200
    
    # Get metrics
    response = client.get("/aeo/metrics")
    data = response.json()
    
    # Verify patterns are tracked
    for pattern in patterns:
        assert pattern.lower() in str(data["query_patterns"]).lower()

def test_confidence_scoring():
    """Test confidence scoring for different query types"""
    queries = [
        {
            "query": "best bbq in gilbert",
            "timestamp": datetime.now().isoformat(),
            "source": "chatgpt",
            "response_type": "local_business",
            "confidence": 0.95,
            "context_relevance": 0.90
        },
        {
            "query": "bbq near me",
            "timestamp": datetime.now().isoformat(),
            "source": "chatgpt",
            "response_type": "location",
            "confidence": 0.70,
            "context_relevance": 0.60
        },
        {
            "query": "big nates family bbq menu",
            "timestamp": datetime.now().isoformat(),
            "source": "chatgpt",
            "response_type": "menu",
            "confidence": 0.85,
            "context_relevance": 0.80
        }
    ]
    
    for query in queries:
        response = client.post("/aeo/log", json=query)
        assert response.status_code == 200
    
    # Get metrics
    response = client.get("/aeo/metrics")
    data = response.json()
    
    # Verify confidence metrics
    assert 0.70 <= data["average_confidence"] <= 0.95
    assert 0.60 <= data["average_context_relevance"] <= 0.90 