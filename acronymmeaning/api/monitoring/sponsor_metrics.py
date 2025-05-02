import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
import logging

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from schema.sponsors import Sponsor, SponsorAcronym
from schema.page_views import PageView
from schema.searches import Search
from db.session import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/sponsors/{sponsor_id}/metrics/views")
async def get_sponsor_views(sponsor_id: int, days: int = 30, db: Session = next(get_db())):
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query page views
        views = db.query(
            func.date(PageView.created_at).label('date'),
            func.count(PageView.id).label('count')
        ).filter(
            and_(
                PageView.page_type == 'sponsor',
                PageView.page_id == str(sponsor_id),
                PageView.created_at >= start_date
            )
        ).group_by(
            func.date(PageView.created_at)
        ).all()
        
        return {
            "sponsor_id": sponsor_id,
            "period": f"last_{days}_days",
            "views": [{"date": str(view.date), "count": view.count} for view in views]
        }
    except Exception as e:
        logger.error(f"Error getting sponsor views: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sponsors/{sponsor_id}/metrics/searches")
async def get_sponsor_searches(sponsor_id: int, days: int = 30, db: Session = next(get_db())):
    try:
        # Get sponsor's acronyms
        sponsor = db.query(Sponsor).filter(Sponsor.id == sponsor_id).first()
        if not sponsor:
            raise HTTPException(status_code=404, detail="Sponsor not found")
            
        acronyms = [acronym.acronym for acronym in sponsor.acronyms]
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query searches
        searches = db.query(
            Search.acronym,
            func.count(Search.id).label('count')
        ).filter(
            and_(
                Search.acronym.in_(acronyms),
                Search.created_at >= start_date
            )
        ).group_by(
            Search.acronym
        ).all()
        
        return {
            "sponsor_id": sponsor_id,
            "period": f"last_{days}_days",
            "searches": [{"acronym": search.acronym, "count": search.count} for search in searches]
        }
    except Exception as e:
        logger.error(f"Error getting sponsor searches: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sponsors/{sponsor_id}/metrics/engagement")
async def get_sponsor_engagement(sponsor_id: int, days: int = 30, db: Session = next(get_db())):
    try:
        # Get views
        views_response = await get_sponsor_views(sponsor_id, days, db)
        total_views = sum(view['count'] for view in views_response['views'])
        
        # Get searches
        searches_response = await get_sponsor_searches(sponsor_id, days, db)
        total_searches = sum(search['count'] for search in searches_response['searches'])
        
        # Calculate engagement score (weighted average)
        engagement_score = (total_views * 0.6) + (total_searches * 0.4)
        
        return {
            "sponsor_id": sponsor_id,
            "period": f"last_{days}_days",
            "total_views": total_views,
            "total_searches": total_searches,
            "engagement_score": engagement_score
        }
    except Exception as e:
        logger.error(f"Error calculating engagement: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 