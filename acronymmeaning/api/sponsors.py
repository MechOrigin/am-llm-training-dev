from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import json
from pathlib import Path
import shutil
import os
from datetime import datetime

router = APIRouter()

# Load sponsor data
SPONSOR_DATA_PATH = Path(__file__).parent.parent / "llm" / "sponsors"
SPONSOR_CONTEXT_PATH = Path(__file__).parent.parent / "llm" / "sponsor_context.json"
SPONSOR_IMAGES_PATH = Path(__file__).parent.parent / "static" / "images" / "sponsors"

# Ensure directories exist
SPONSOR_IMAGES_PATH.mkdir(parents=True, exist_ok=True)

@router.get("/sponsors/")
async def get_sponsors():
    """Get list of all sponsors"""
    try:
        sponsors = []
        for sponsor_file in SPONSOR_DATA_PATH.glob("*.json"):
            if sponsor_file.name != "sponsor_template.json":
                with open(sponsor_file) as f:
                    sponsors.append(json.load(f))
        return {"sponsors": sponsors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sponsors/{sponsor_id}")
async def get_sponsor(sponsor_id: str):
    """Get specific sponsor information"""
    try:
        sponsor_file = SPONSOR_DATA_PATH / f"{sponsor_id}.json"
        if not sponsor_file.exists():
            raise HTTPException(status_code=404, detail="Sponsor not found")
        with open(sponsor_file) as f:
            return json.load(f)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sponsors/{sponsor_id}/acronyms")
async def get_sponsor_acronyms(sponsor_id: str):
    """Get acronyms related to a specific sponsor"""
    try:
        with open(SPONSOR_CONTEXT_PATH) as f:
            context_data = json.load(f)
        
        sponsor_context = next(
            (item for item in context_data["sponsor_mappings"] if item["sponsor_id"] == sponsor_id),
            None
        )
        
        if not sponsor_context:
            raise HTTPException(status_code=404, detail="Sponsor context not found")
        
        return {"acronyms": sponsor_context["acronyms"]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sponsors/upload-logo/{sponsor_id}")
async def upload_sponsor_logo(
    sponsor_id: str,
    file: UploadFile = File(...)
):
    """Upload a sponsor logo"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{sponsor_id}_{timestamp}{file_extension}"
        
        # Save file
        file_path = SPONSOR_IMAGES_PATH / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update sponsor JSON with logo URL
        sponsor_file = SPONSOR_DATA_PATH / f"{sponsor_id}.json"
        if sponsor_file.exists():
            with open(sponsor_file, "r") as f:
                sponsor_data = json.load(f)
            
            sponsor_data["logo_url"] = f"/static/images/sponsors/{filename}"
            
            with open(sponsor_file, "w") as f:
                json.dump(sponsor_data, f, indent=4)
        
        return {"message": "Logo uploaded successfully", "logo_url": f"/static/images/sponsors/{filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 