from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from schema.sponsors import Base, Sponsor, SponsorAcronym
from schema.page_views import PageView
from schema.searches import Search

# Database connection
DATABASE_URL = "sqlite:///acronymmeaning.db"
engine = create_engine(DATABASE_URL)

def init_db():
    """Initialize the database with all required tables"""
    try:
        # Create all tables
        Base.metadata.create_all(engine)
        print("Database tables created successfully")
        
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Add some test data if needed
        test_sponsor = Sponsor(
            company_name="Test Sponsor",
            description="A test sponsor for testing purposes",
            key_products_services=["Test Product 1", "Test Service 1"],
            relevant_acronyms=[{"acronym": "TST", "meaning": "Test Sponsor Technology"}],
            industry_focus=["Testing", "Technology"],
            contact_information={
                "website": "https://testsponsor.com",
                "email": "test@testsponsor.com"
            },
            llm_training_context={
                "key_phrases": ["test phrase"],
                "industry_terms": ["test term"],
                "brand_voice": "Test brand voice"
            }
        )
        
        session.add(test_sponsor)
        session.commit()
        
        # Add test acronym
        test_acronym = SponsorAcronym(
            sponsor_id=1,  # Assuming this is the ID of the test sponsor
            acronym="TST",
            context="Test Sponsor Technology",
            relevance_score=0.95,
            usage_contexts=["testing", "development"]
        )
        
        session.add(test_acronym)
        session.commit()
        
        print("Test data added successfully")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_db() 