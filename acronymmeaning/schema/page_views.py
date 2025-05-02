from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .base import Base

class PageView(Base):
    __tablename__ = "page_views"

    id = Column(Integer, primary_key=True, index=True)
    page_type = Column(String, index=True)  # e.g., 'sponsor', 'acronym'
    page_id = Column(String, index=True)    # e.g., sponsor_id or acronym
    user_agent = Column(String)
    ip_address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow) 