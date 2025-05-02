from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Search(Base):
    __tablename__ = "searches"

    id = Column(Integer, primary_key=True, index=True)
    search_term = Column(String, index=True)
    ip_address = Column(String)
    user_agent = Column(String)
    search_results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow) 