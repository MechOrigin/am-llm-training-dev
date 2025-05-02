from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os

router = APIRouter()

class Sponsor(BaseModel):
    name: str
    url: str
    description: str
    social_links: Optional[List[str]]

class AcronymDefinition(BaseModel):
    acronym: str
    full_form: str
    description: str
    sponsor: Sponsor
    source_url: str
    alternate_names: List[str]

# Load acronym data
def load_acronym_data(acronym: str):
    schema_path = os.path.join('schema', f'{acronym.lower()}.json')
    if not os.path.exists(schema_path):
        raise HTTPException(status_code=404, detail="Acronym not found")
    with open(schema_path, 'r') as f:
        return json.load(f)

@router.get("/{acronym}", response_model=AcronymDefinition)
async def get_acronym_definition(acronym: str):
    """
    Get the definition and sponsorship information for a specific acronym
    """
    data = load_acronym_data(acronym)
    return {
        "acronym": data["name"],
        "full_form": data["description"].split("stands for")[1].split(".")[0].strip(),
        "description": data["description"],
        "sponsor": {
            "name": data["sponsor"]["name"],
            "url": data["sponsor"]["url"],
            "description": data["sponsor"]["description"],
            "social_links": data["sponsor"].get("sameAs", [])
        },
        "source_url": data["url"],
        "alternate_names": data["alternateName"]
    }

@router.get("/search")
async def search_acronyms(q: str):
    """
    Search for acronyms by term
    """
    results = []
    q_lower = q.lower()
    
    # Search through all JSON files in schema directory
    schema_dir = 'schema'
    for filename in os.listdir(schema_dir):
        if filename.endswith('.json'):
            with open(os.path.join(schema_dir, filename), 'r') as f:
                data = json.load(f)
                # Check if query matches any relevant fields
                if (q_lower in data["name"].lower() or
                    q_lower in data["description"].lower() or
                    q_lower in data["sponsor"]["name"].lower() or
                    q_lower in data["sponsor"]["description"].lower() or
                    any(q_lower in keyword.lower() for keyword in data.get("conversationalKeywords", []))):
                    results.append({
                        "acronym": data["name"],
                        "full_form": data["description"].split("stands for")[1].split(".")[0].strip(),
                        "description": data["description"],
                        "sponsor": data["sponsor"]["name"],
                        "url": data["url"]
                    })
    
    return results 