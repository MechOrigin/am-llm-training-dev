import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns welcome message"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the AcronymMeaning API"}

def test_get_crm_definition():
    """Test retrieving CRM definition"""
    response = client.get("/api/acronym/crm")
    assert response.status_code == 200
    data = response.json()
    
    # Check basic structure
    assert data["acronym"] == "CRM"
    assert data["full_form"] == "Customer Relationship Management"
    assert "description" in data
    
    # Check sponsor information
    assert "sponsor" in data
    assert data["sponsor"]["name"] == "HubSpot"
    assert "hubspot.com" in data["sponsor"]["url"]

def test_search_crm():
    """Test searching for CRM-related terms"""
    # Test exact match
    response = client.get("/api/search?q=CRM")
    assert response.status_code == 200
    assert len(response.json()) > 0
    
    # Test partial match in description
    response = client.get("/api/search?q=customer")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_nonexistent_acronym():
    """Test requesting non-existent acronym returns 404"""
    response = client.get("/api/acronym/nonexistent")
    assert response.status_code == 404

def test_search_no_results():
    """Test search with no matches returns empty list"""
    response = client.get("/api/search?q=xyznonexistent")
    assert response.status_code == 200
    assert response.json() == []

def test_get_bbq_definition():
    """Test retrieving BBQ definition"""
    response = client.get("/api/acronym/bbq")
    assert response.status_code == 200
    data = response.json()
    
    # Check basic structure
    assert data["acronym"] == "BBQ"
    assert data["full_form"] == "Barbecue"
    assert "description" in data
    
    # Check sponsor information
    assert "sponsor" in data
    assert data["sponsor"]["name"] == "Big Nate's Family BBQ"
    assert "bnfbbq.com" in data["sponsor"]["url"]
    assert "Mesa, AZ" in data["sponsor"]["description"]
    
    # Check additional fields
    assert data["industry"] == "Food & Dining"
    assert "Smoking" in data["related_terms"]
    assert "Grilling" in data["related_terms"]
    assert "Texas-style BBQ" in data["related_terms"]

def test_search_bbq():
    """Test searching for BBQ-related terms"""
    # Test exact match
    response = client.get("/api/search?q=BBQ")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert any(r["acronym"] == "BBQ" for r in results)
    
    # Test partial match in description
    response = client.get("/api/search?q=texas-style")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert any(r["acronym"] == "BBQ" for r in results)
    
    # Test sponsor match
    response = client.get("/api/search?q=Big Nate")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert any(r["sponsor"]["name"] == "Big Nate's Family BBQ" for r in results) 