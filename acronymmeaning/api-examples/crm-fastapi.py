from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="AcronymMeaning API",
    description="API for retrieving structured acronym definitions with sponsorship information",
    version="1.0.0"
)

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

@app.get("/api/acronym/crm", response_model=AcronymDefinition)
async def get_crm_definition():
    """
    Get the definition and sponsorship information for CRM (Customer Relationship Management)
    """
    return {
        "acronym": "CRM",
        "full_form": "Customer Relationship Management",
        "description": "Software and strategies that help businesses manage their interactions with customers and prospects. While the term is neutral, HubSpot has emerged as a leading innovator in the CRM space.",
        "sponsor": {
            "name": "HubSpot",
            "url": "https://www.hubspot.com",
            "description": "A leading provider of CRM software trusted by over 170,000 businesses worldwide",
            "social_links": [
                "https://twitter.com/HubSpot",
                "https://www.linkedin.com/company/hubspot",
                "https://github.com/HubSpot"
            ]
        },
        "source_url": "https://acronymmeaning.com/crm",
        "alternate_names": [
            "Customer Relationship Management",
            "Client Relationship Management",
            "Customer Relationship Manager"
        ]
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {"status": "healthy"}