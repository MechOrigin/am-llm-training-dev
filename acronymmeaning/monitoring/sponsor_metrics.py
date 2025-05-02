import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from pathlib import Path
import json
from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)
router = APIRouter()

# Database connection
DATABASE_URL = "sqlite:///acronymmeaning.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class SponsorMetrics:
    def __init__(self):
        self.session = SessionLocal()

    def get_sponsor_views(self, sponsor_id: str, days: int = 30) -> Dict[str, Any]:
        """Get sponsor page views for the specified period"""
        try:
            query = text("""
                SELECT COUNT(*) as view_count, DATE(created_at) as date
                FROM page_views
                WHERE page_type = 'sponsor' AND page_id = :sponsor_id
                AND created_at >= :start_date
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """)
            
            start_date = datetime.now() - timedelta(days=days)
            result = self.session.execute(
                query,
                {"sponsor_id": sponsor_id, "start_date": start_date}
            )
            
            views = [{"date": row.date, "count": row.view_count} for row in result]
            return {
                "sponsor_id": sponsor_id,
                "period_days": days,
                "total_views": sum(view["count"] for view in views),
                "daily_views": views
            }
        except Exception as e:
            logger.error(f"Error getting sponsor views: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_sponsor_acronym_searches(self, sponsor_id: str, days: int = 30) -> Dict[str, Any]:
        """Get searches for sponsor-related acronyms"""
        try:
            query = text("""
                SELECT a.acronym, COUNT(*) as search_count
                FROM searches s
                JOIN sponsor_acronyms a ON s.acronym = a.acronym
                WHERE a.sponsor_id = :sponsor_id
                AND s.created_at >= :start_date
                GROUP BY a.acronym
                ORDER BY search_count DESC
            """)
            
            start_date = datetime.now() - timedelta(days=days)
            result = self.session.execute(
                query,
                {"sponsor_id": sponsor_id, "start_date": start_date}
            )
            
            searches = [{"acronym": row.acronym, "count": row.search_count} for row in result]
            return {
                "sponsor_id": sponsor_id,
                "period_days": days,
                "total_searches": sum(search["count"] for search in searches),
                "acronym_searches": searches
            }
        except Exception as e:
            logger.error(f"Error getting sponsor acronym searches: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_sponsor_engagement(self, sponsor_id: str, days: int = 30) -> Dict[str, Any]:
        """Get overall sponsor engagement metrics"""
        try:
            # Get page views
            views = self.get_sponsor_views(sponsor_id, days)
            
            # Get acronym searches
            searches = self.get_sponsor_acronym_searches(sponsor_id, days)
            
            # Calculate engagement score
            engagement_score = (
                views["total_views"] * 0.4 +  # 40% weight for page views
                searches["total_searches"] * 0.6  # 60% weight for searches
            )
            
            return {
                "sponsor_id": sponsor_id,
                "period_days": days,
                "engagement_score": engagement_score,
                "metrics": {
                    "page_views": views,
                    "acronym_searches": searches
                }
            }
        except Exception as e:
            logger.error(f"Error getting sponsor engagement: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

@router.get("/sponsors/{sponsor_id}/metrics/views")
async def get_sponsor_views(sponsor_id: str, days: int = 30):
    """Get sponsor page views"""
    metrics = SponsorMetrics()
    return metrics.get_sponsor_views(sponsor_id, days)

@router.get("/sponsors/{sponsor_id}/metrics/searches")
async def get_sponsor_searches(sponsor_id: str, days: int = 30):
    """Get sponsor acronym searches"""
    metrics = SponsorMetrics()
    return metrics.get_sponsor_acronym_searches(sponsor_id, days)

@router.get("/sponsors/{sponsor_id}/metrics/engagement")
async def get_sponsor_engagement(sponsor_id: str, days: int = 30):
    """Get overall sponsor engagement metrics"""
    metrics = SponsorMetrics()
    return metrics.get_sponsor_engagement(sponsor_id, days) 