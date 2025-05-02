from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class PageView(Base):
    __tablename__ = "page_views"

    id = Column(Integer, primary_key=True, index=True)
    page_url = Column(String, index=True)
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow) 