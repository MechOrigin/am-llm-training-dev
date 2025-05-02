from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
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

    # Add relationship with SponsorAcronym
    acronyms = relationship("SponsorAcronym", back_populates="sponsor")

class SponsorAcronym(Base):
    __tablename__ = "sponsor_acronyms"

    id = Column(Integer, primary_key=True, index=True)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"))
    acronym = Column(String, index=True)
    meaning = Column(String)
    relevance_score = Column(Integer)
    usage_contexts = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add relationship with Sponsor
    sponsor = relationship("Sponsor", back_populates="acronyms") 