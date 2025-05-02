from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Search(Base):
    __tablename__ = "searches"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, index=True)
    acronym = Column(String, index=True)
    user_agent = Column(String)
    ip_address = Column(String)
    results = Column(JSON)  # Store search results for analysis
    created_at = Column(DateTime, default=datetime.utcnow) 