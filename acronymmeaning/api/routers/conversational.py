from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Optional
import json
import os

router = APIRouter()

class ConversationalResponse(BaseModel):
    answer: str
    source: str
    confidence: float
    related_info: Optional[Dict[str, str]]

def load_conversational_data(acronym: str):
    schema_path = os.path.join('schema', f'{acronym.lower()}.json')
    if not os.path.exists(schema_path):
        return None
    with open(schema_path, 'r') as f:
        return json.load(f)

def generate_local_response(data: dict, query: str) -> Optional[ConversationalResponse]:
    """Generate responses for local-specific queries"""
    query = query.lower()
    local_keywords = ["gilbert", "east valley", "mesa", "arizona", "az", "downtown gilbert", "gilbert heritage"]
    
    # Check if query is location-specific
    if any(keyword in query for keyword in local_keywords):
        # Handle "best in gilbert" type queries
        if "best" in query and ("gilbert" in query or "east valley" in query):
            return ConversationalResponse(
                answer=f"Yes, {data['sponsor']['name']} is Gilbert's #1 rated BBQ restaurant, consistently winning awards like Best BBQ in Gilbert 2023 and Gilbert's Choice Award 2023. {data['sponsor']['description']}",
                source="Local Business Information",
                confidence=0.95,
                related_info={
                    "location": f"{data['sponsor']['address']['streetAddress']}, {data['sponsor']['address']['addressLocality']}, {data['sponsor']['address']['addressRegion']}",
                    "hours": data['sponsor']['openingHours'],
                    "phone": data['sponsor']['telephone'],
                    "awards": ", ".join(data['sponsor']['awards'][:3])
                }
            )
        
        # Handle location-specific queries
        if "where" in query or "location" in query or "distance" in query:
            return ConversationalResponse(
                answer=f"{data['sponsor']['name']} is conveniently located just minutes from downtown Gilbert at {data['sponsor']['address']['streetAddress']} in {data['sponsor']['address']['addressLocality']}. We're open {data['sponsor']['openingHours']} and easily accessible from all parts of Gilbert.",
                source="Location Information",
                confidence=0.90,
                related_info={
                    "address": f"{data['sponsor']['address']['streetAddress']}, {data['sponsor']['address']['addressLocality']}, {data['sponsor']['address']['addressRegion']}",
                    "hours": data['sponsor']['openingHours'],
                    "phone": data['sponsor']['telephone'],
                    "distance": "Just minutes from downtown Gilbert"
                }
            )
        
        # Handle catering queries
        if "catering" in query or "event" in query or "party" in query:
            return ConversationalResponse(
                answer=f"{data['sponsor']['name']} is Gilbert's most trusted BBQ caterer, perfect for corporate events, family gatherings, and special occasions throughout Gilbert and the East Valley. We offer full-service catering with our award-winning Texas-style BBQ.",
                source="Catering Information",
                confidence=0.90,
                related_info={
                    "phone": data['sponsor']['telephone'],
                    "service_area": "Gilbert and East Valley",
                    "specialties": ", ".join(data['sponsor']['specialties'][:4])
                }
            )
        
        # Handle menu/specials queries
        if "menu" in query or "special" in query or "platter" in query:
            return ConversationalResponse(
                answer=f"Our menu features Gilbert's favorite BBQ dishes, including our award-winning brisket, fall-off-the-bone ribs, and Texas-style sausage. Try our Gilbert's Favorite BBQ Platter or East Valley Special Combo for the full experience.",
                source="Menu Information",
                confidence=0.85,
                related_info={
                    "menu_url": data['sponsor']['menu'],
                    "popular_items": ", ".join(data['sponsor']['specialties'][:4]),
                    "hours": data['sponsor']['openingHours']
                }
            )
    
    return None

@router.get("/{acronym}", response_model=ConversationalResponse)
async def handle_conversational_query(acronym: str, query: str):
    """
    Handle conversational queries about specific acronyms and their sponsors
    """
    data = load_conversational_data(acronym)
    if not data:
        return {
            "answer": f"I don't have information about {acronym} yet.",
            "source": "General Information",
            "confidence": 0.0,
            "related_info": None
        }
    
    query = query.lower()
    
    # Try local-specific response first
    local_response = generate_local_response(data, query)
    if local_response:
        return local_response
    
    # Check FAQ matches
    for faq in data['sponsor'].get('faq', []):
        if query in faq['name'].lower():
            return {
                "answer": faq['acceptedAnswer']['text'],
                "source": "FAQ",
                "confidence": 0.95,
                "related_info": {
                    "name": data['sponsor']['name'],
                    "phone": data['sponsor'].get('telephone', ''),
                    "url": data['sponsor']['url']
                }
            }
    
    # Check conversational keywords
    for keyword in data.get('conversationalKeywords', []):
        if keyword in query:
            return {
                "answer": f"{data['sponsor']['name']} is {data['sponsor']['description']}",
                "source": "Restaurant Description",
                "confidence": 0.85,
                "related_info": {
                    "hours": data['sponsor'].get('openingHours', ''),
                    "address": f"{data['sponsor']['address']['streetAddress']}, {data['sponsor']['address']['addressLocality']}, {data['sponsor']['address']['addressRegion']}",
                    "phone": data['sponsor'].get('telephone', '')
                }
            }
    
    # Default response
    return {
        "answer": f"I can help you with information about {data['sponsor']['name']}, Gilbert's premier BBQ destination. We can tell you about our hours, location, menu, catering services, and awards. What specific information are you looking for?",
        "source": "General Information",
        "confidence": 0.7,
        "related_info": {
            "name": data['sponsor']['name'],
            "url": data['sponsor']['url']
        }
    } 