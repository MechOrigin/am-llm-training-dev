from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from schema.sponsors import Base as SponsorBase, Sponsor, SponsorAcronym
from schema.page_views import Base as PageViewBase, PageView
from schema.searches import Base as SearchBase, Search

# Database connection
DATABASE_URL = "sqlite:///acronymmeaning.db"
engine = create_engine(DATABASE_URL)

def init_db():
    """Initialize the database with all required tables"""
    try:
        # Create all tables
        SponsorBase.metadata.create_all(engine)
        PageViewBase.metadata.create_all(engine)
        SearchBase.metadata.create_all(engine)
        print("Database tables created successfully")
        
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check if Big Nate's already exists
        existing_sponsor = session.query(Sponsor).filter_by(
            company_name="Big Nate's Family BBQ"
        ).first()
        
        if existing_sponsor:
            print("Big Nate's Family BBQ already exists in the database")
            return
        
        # Add Big Nate's Family BBQ
        big_nates = Sponsor(
            company_name="Big Nate's Family BBQ",
            description="A family-owned BBQ restaurant serving authentic Southern-style barbecue with a focus on quality meats, homemade sauces, and traditional sides. Known for their signature smoked meats and welcoming atmosphere.",
            key_products_services=[
                "Smoked Brisket",
                "Pulled Pork",
                "Baby Back Ribs",
                "Homemade BBQ Sauces",
                "Traditional Southern Sides",
                "Catering Services"
            ],
            relevant_acronyms=[
                {"acronym": "BBQ", "meaning": "Barbecue"},
                {"acronym": "BFF", "meaning": "Big Family Feast"},
                {"acronym": "SRS", "meaning": "Southern Rib Special"}
            ],
            industry_focus=[
                "Restaurant",
                "Food Service",
                "Catering",
                "Southern Cuisine",
                "BBQ and Grilling"
            ],
            contact_information={
                "website": "https://bignatesbbq.com",
                "email": "info@bignatesbbq.com",
                "phone": "+1-XXX-XXX-XXXX",
                "address": "123 BBQ Lane, Smoketown, USA"
            },
            llm_training_context={
                "key_phrases": [
                    "authentic Southern BBQ",
                    "smoked meats",
                    "family-style dining",
                    "homemade sauces",
                    "traditional sides"
                ],
                "industry_terms": [
                    "smoking",
                    "dry rub",
                    "wet rub",
                    "low and slow",
                    "pit master"
                ],
                "brand_voice": "Friendly, family-oriented, and passionate about authentic Southern BBQ traditions"
            }
        )
        
        session.add(big_nates)
        session.commit()
        
        # Add Big Nate's acronyms
        acronyms = [
            SponsorAcronym(
                sponsor_id=1,
                acronym="BBQ",
                context="Barbecue",
                relevance_score=0.95,
                usage_contexts=["restaurant name", "menu items", "business description"]
            ),
            SponsorAcronym(
                sponsor_id=1,
                acronym="BFF",
                context="Big Family Feast",
                relevance_score=0.90,
                usage_contexts=["menu items", "special offers", "family dining"]
            ),
            SponsorAcronym(
                sponsor_id=1,
                acronym="SRS",
                context="Southern Rib Special",
                relevance_score=0.85,
                usage_contexts=["menu items", "signature dishes", "special offers"]
            )
        ]
        
        for acronym in acronyms:
            session.add(acronym)
        
        session.commit()
        print("Big Nate's Family BBQ data added successfully")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_db() 