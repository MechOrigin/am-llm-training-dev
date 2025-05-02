import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import json
import os

# Import your FastAPI app
from acronymmeaning.api.main import app

client = TestClient(app)

# Test data
TEST_SPONSOR = {
    "company_name": "Test Sponsor",
    "description": "A test sponsor for testing purposes",
    "key_products_services": ["Test Product 1", "Test Service 1"],
    "relevant_acronyms": [
        {
            "acronym": "TST",
            "meaning": "Test Sponsor Technology",
            "context": "Test context"
        }
    ],
    "industry_focus": ["Testing", "Technology"],
    "contact_information": {
        "website": "https://testsponsor.com",
        "email": "test@testsponsor.com"
    },
    "llm_training_context": {
        "key_phrases": ["test phrase"],
        "industry_terms": ["test term"],
        "brand_voice": "Test brand voice"
    }
}

@pytest.fixture
def setup_test_sponsor():
    # Create test sponsor file
    sponsor_dir = Path("acronymmeaning/llm/sponsors")
    sponsor_dir.mkdir(parents=True, exist_ok=True)
    
    with open(sponsor_dir / "test_sponsor.json", "w") as f:
        json.dump(TEST_SPONSOR, f)
    
    yield
    
    # Cleanup
    if os.path.exists(sponsor_dir / "test_sponsor.json"):
        os.remove(sponsor_dir / "test_sponsor.json")

def test_get_sponsors(setup_test_sponsor):
    response = client.get("/sponsors/")
    assert response.status_code == 200
    data = response.json()
    assert "sponsors" in data
    assert len(data["sponsors"]) > 0
    assert any(sponsor["company_name"] == "Test Sponsor" for sponsor in data["sponsors"])

def test_get_specific_sponsor(setup_test_sponsor):
    response = client.get("/sponsors/test_sponsor")
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "Test Sponsor"
    assert data["description"] == "A test sponsor for testing purposes"

def test_get_sponsor_acronyms(setup_test_sponsor):
    response = client.get("/sponsors/test_sponsor/acronyms")
    assert response.status_code == 200
    data = response.json()
    assert "acronyms" in data
    assert len(data["acronyms"]) > 0
    assert any(acronym["acronym"] == "TST" for acronym in data["acronyms"])

def test_sponsor_not_found():
    response = client.get("/sponsors/nonexistent_sponsor")
    assert response.status_code == 404

def test_sponsor_acronyms_not_found():
    response = client.get("/sponsors/nonexistent_sponsor/acronyms")
    assert response.status_code == 404

def test_sponsor_template_exists():
    template_path = Path("acronymmeaning/llm/sponsors/sponsor_template.json")
    assert template_path.exists()
    
    with open(template_path) as f:
        template = json.load(f)
        assert "company_name" in template
        assert "description" in template
        assert "key_products_services" in template
        assert "relevant_acronyms" in template
        assert "industry_focus" in template
        assert "contact_information" in template
        assert "llm_training_context" in template 