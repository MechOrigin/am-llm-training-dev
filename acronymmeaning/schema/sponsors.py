from sqlalchemy import Column, Integer, String, JSON, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Sponsor(Base):
    __tablename__ = "sponsors"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, unique=True, index=True)
    description = Column(String)
    key_products_services = Column(JSON)
    relevant_acronyms = Column(JSON)
    industry_focus = Column(JSON)
    contact_information = Column(JSON)
    llm_training_context = Column(JSON)
    logo_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SponsorAcronym(Base):
    __tablename__ = "sponsor_acronyms"

    id = Column(Integer, primary_key=True, index=True)
    sponsor_id = Column(Integer, index=True)
    acronym = Column(String, index=True)
    context = Column(String)
    relevance_score = Column(Float)
    usage_contexts = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 