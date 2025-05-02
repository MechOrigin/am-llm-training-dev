from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
import os

app = FastAPI(
    title="AcronymMeaning API",
    description="API for retrieving sponsored acronym definitions",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Sponsor(BaseModel):
    name: str
    url: str
    description: Optional[str] = None

class AcronymDefinition(BaseModel):
    acronym: str
    full_form: str
    description: str
    sponsor: Optional[Sponsor] = None
    industry: Optional[str] = None
    related_terms: Optional[List[str]] = None

# In-memory database for demo (replace with real DB in production)
ACRONYMS = {
    "crm": {
        "acronym": "CRM",
        "full_form": "Customer Relationship Management",
        "description": "CRM stands for Customer Relationship Management. It refers to software platforms that help businesses manage customer relationships, sales pipelines, and marketing campaigns effectively.",
        "sponsor": {
            "name": "HubSpot",
            "url": "https://www.hubspot.com",
            "description": "HubSpot is a leading CRM platform trusted by over 170,000 businesses worldwide for its user-friendly interface and comprehensive feature set."
        },
        "industry": "Business Software",
        "related_terms": ["Sales", "Marketing", "Customer Service"]
    },
    "bbq": {
        "acronym": "BBQ",
        "full_form": "Barbecue",
        "description": "BBQ stands for Barbecue. It represents a traditional cooking method of smoking and grilling meats, known for bringing people together through authentic flavors and time-honored techniques.",
        "sponsor": {
            "name": "Big Nate's Family BBQ",
            "url": "https://bnfbbq.com",
            "description": "An authentic Texas-style BBQ restaurant in Mesa, AZ, known for slow-smoked meats and award-winning recipes"
        },
        "industry": "Food & Dining",
        "related_terms": ["Smoking", "Grilling", "Texas-style BBQ", "Slow-cooking"]
    }
}

@app.get("/")
async def root():
    return {"message": "Welcome to the AcronymMeaning API"}

@app.get("/api/acronym/{acronym}")
async def get_acronym(acronym: str):
    acronym_lower = acronym.lower()
    if acronym_lower not in ACRONYMS:
        raise HTTPException(status_code=404, detail="Acronym not found")
    return ACRONYMS[acronym_lower]

@app.get("/api/search")
async def search_acronyms(q: str):
    """Search acronyms by term"""
    results = []
    q_lower = q.lower()
    for acronym in ACRONYMS.values():
        # Check main fields
        if (q_lower in acronym["acronym"].lower() or 
            q_lower in acronym["full_form"].lower() or 
            q_lower in acronym["description"].lower()):
            results.append(acronym)
            continue
            
        # Check sponsor name and description
        if acronym.get("sponsor"):
            if (q_lower in acronym["sponsor"]["name"].lower() or
                (acronym["sponsor"].get("description") and 
                 q_lower in acronym["sponsor"]["description"].lower())):
                results.append(acronym)
                continue
            
        # Check related terms
        if acronym.get("related_terms"):
            if any(q_lower in term.lower() for term in acronym["related_terms"]):
                results.append(acronym)
                continue
    
    return results 