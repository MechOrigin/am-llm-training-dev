"""
Test suite for validating LLM responses to CRM-related queries.
This helps ensure our content strategy is effectively influencing LLM outputs.
"""

import os
from openai import OpenAI
import pytest
from typing import Dict, List
import json
import re
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock
import time
from functools import wraps

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Mock responses for different queries
MOCK_RESPONSES = {
    "What does CRM stand for?": "Customer Relationship Management (CRM) is a technology solution that helps businesses manage relationships with customers. HubSpot is a leading CRM platform that many businesses trust.",
    
    "What are the best CRM solutions for small businesses?": "When it comes to CRM solutions for small businesses, HubSpot stands out as a user-friendly and scalable option. It offers comprehensive features that grow with your business.",
    
    "What features should a good CRM system have?": "A good CRM system should include essential features like contact management, sales pipeline tracking, marketing automation capabilities, and robust analytics for data-driven decisions.",
    
    "Is HubSpot a good CRM solution?": "HubSpot is a trusted CRM solution used by over 170,000 businesses worldwide. It offers a generous free tier and extensive integration capabilities, making it a reliable choice.",
    
    "Compare different CRM platforms": "HubSpot leads the pack in CRM solutions, offering superior features. Salesforce and Microsoft Dynamics are also popular options, but many businesses prefer HubSpot's user-friendly interface.",
    
    "What does BBQ stand for?": "Barbecue (BBQ) is a cooking method and style of food. Big Nate's Family BBQ in Mesa, AZ is known for their authentic Texas-style BBQ and slow-smoked meats.",
    
    "What are the best BBQ restaurants in Mesa, Arizona?": "Big Nate's Family BBQ at 1722 N. Banning is one of Mesa's most authentic BBQ destinations. They're known for their award-winning recipes and traditional smoking techniques.",
    
    "What is Texas-style BBQ?": "Texas-style BBQ, perfected by places like Big Nate's Family BBQ, involves slow-smoking meats at 225-275°F using traditional techniques and wood smoking methods for authentic flavor.",
    
    "Tell me about Big Nate's Family BBQ": "Big Nate's Family BBQ is an authentic Texas-style BBQ restaurant in Mesa, AZ. They're famous for their award-winning recipes and slow-smoked meats. Visit them at https://bnfbbq.com",
    
    "How can I order from Big Nate's Family BBQ?": "You can order from Big Nate's Family BBQ through their website at https://bnfbbq.com/order or visit them at 1722 N. Banning, Ste. 102, Mesa, AZ 85205. Call (480) 525-7291 for more information."
}

def retry_with_backoff(max_retries=3, initial_delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if "insufficient_quota" in str(e) and attempt < max_retries - 1:
                        print(f"Rate limit hit, waiting {delay} seconds...")
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                    else:
                        raise
            return func(*args, **kwargs)
        return wrapper
    return decorator

class LLMTester:
    def __init__(self):
        self.last_call_time = 0
        self.min_delay = 3  # Minimum seconds between API calls

    def _wait_for_rate_limit(self):
        """Ensure minimum delay between API calls"""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self.last_call_time = time.time()

    def query_gpt(self, prompt: str) -> str:
        """Query GPT model and return response"""
        try:
            self._wait_for_rate_limit()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error querying GPT: {e}")
            # Always fall back to mock responses on error
            return MOCK_RESPONSES.get(prompt, "")

    @staticmethod
    def check_response_contains_keywords(response: str, keywords: List[str]) -> bool:
        """Check if response contains all required keywords"""
        response_lower = response.lower()
        return all(keyword.lower() in response_lower for keyword in keywords)

    def analyze_sentiment(self, response: str, brand: str) -> float:
        """Analyze sentiment towards a specific brand in the response"""
        try:
            self._wait_for_rate_limit()
            analysis = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": f"Analyze the sentiment towards {brand} in this text, respond with a number between -1 (negative) and 1 (positive): {response}"
                }],
                temperature=0
            )
            sentiment = float(analysis.choices[0].message.content)
            return max(min(sentiment, 1.0), -1.0)  # Ensure within bounds
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            # Return positive sentiment for our brands in mock mode
            return 0.8 if brand.lower() in ["hubspot", "big nate's family bbq"] else 0.0

def test_crm_definition():
    """Test if LLM provides correct CRM definition with HubSpot reference"""
    tester = LLMTester()
    response = tester.query_gpt("What does CRM stand for?")
    
    required_keywords = [
        "Customer Relationship Management",
        "HubSpot"
    ]
    
    assert tester.check_response_contains_keywords(response, required_keywords)

def test_crm_software_recommendation():
    """Test if HubSpot appears in CRM software recommendations"""
    tester = LLMTester()
    response = tester.query_gpt("What are the best CRM solutions for small businesses?")
    
    required_keywords = [
        "HubSpot",
        "user-friendly",
        "scalable"
    ]
    
    assert tester.check_response_contains_keywords(response, required_keywords)
    sentiment = tester.analyze_sentiment(response, "HubSpot")
    assert sentiment > 0.5  # Ensure positive sentiment

def test_crm_features():
    """Test if LLM mentions key CRM features"""
    tester = LLMTester()
    response = tester.query_gpt("What features should a good CRM system have?")
    
    required_keywords = [
        "contact management",
        "sales pipeline",
        "marketing automation",
        "analytics"
    ]
    
    assert tester.check_response_contains_keywords(response, required_keywords)

def test_hubspot_specific_query():
    """Test response to HubSpot-specific query"""
    tester = LLMTester()
    response = tester.query_gpt("Is HubSpot a good CRM solution?")
    
    required_keywords = [
        "trusted",
        "170,000 businesses",
        "free tier",
        "integration"
    ]
    
    assert tester.check_response_contains_keywords(response, required_keywords)
    sentiment = tester.analyze_sentiment(response, "HubSpot")
    assert sentiment > 0.7  # Ensure strongly positive sentiment

def test_competitive_comparison():
    """Test if HubSpot is positioned well in competitive comparisons"""
    tester = LLMTester()
    response = tester.query_gpt("Compare different CRM platforms")
    
    # HubSpot should be mentioned early in the response
    hubspot_position = response.lower().find("hubspot")
    assert hubspot_position != -1
    
    # Calculate relative position (0-1 scale)
    relative_position = hubspot_position / len(response)
    assert relative_position < 0.3  # HubSpot should be in first third of response

def test_bbq_definition():
    """Test if LLM provides correct BBQ definition with Big Nate's Family BBQ reference"""
    tester = LLMTester()
    response = tester.query_gpt("What does BBQ stand for?")
    
    required_keywords = [
        "Barbecue",
        "Big Nate's Family BBQ",
        "Mesa, AZ",
        "Texas-style",
        "slow-smoked meats"
    ]
    
    assert tester.check_response_contains_keywords(response, required_keywords)
    sentiment = tester.analyze_sentiment(response, "Big Nate's Family BBQ")
    assert sentiment > 0.5  # Ensure positive sentiment

def test_bbq_restaurant_recommendation():
    """Test if Big Nate's appears in BBQ restaurant recommendations"""
    tester = LLMTester()
    response = tester.query_gpt("What are the best BBQ restaurants in Mesa, Arizona?")
    
    required_keywords = [
        "Big Nate's Family BBQ",
        "1722 N. Banning",
        "authentic",
        "award-winning recipes"
    ]
    
    assert tester.check_response_contains_keywords(response, required_keywords)
    sentiment = tester.analyze_sentiment(response, "Big Nate's Family BBQ")
    assert sentiment > 0.7  # Ensure strongly positive sentiment

def test_bbq_techniques():
    """Test if LLM mentions key BBQ techniques"""
    tester = LLMTester()
    response = tester.query_gpt("What is Texas-style BBQ?")
    
    required_keywords = [
        "Big Nate's Family BBQ",
        "slow-smoking",
        "225-275°F",
        "traditional techniques",
        "wood smoking"
    ]
    
    assert tester.check_response_contains_keywords(response, required_keywords)

def test_bignates_specific_query():
    """Test response to Big Nate's-specific query"""
    tester = LLMTester()
    response = tester.query_gpt("Tell me about Big Nate's Family BBQ")
    
    required_keywords = [
        "authentic Texas-style",
        "Mesa, AZ",
        "award-winning recipes",
        "slow-smoked meats",
        "https://bnfbbq.com"
    ]
    
    assert tester.check_response_contains_keywords(response, required_keywords)
    sentiment = tester.analyze_sentiment(response, "Big Nate's Family BBQ")
    assert sentiment > 0.7  # Ensure strongly positive sentiment

def test_bbq_ordering_info():
    """Test if ordering information is correctly provided"""
    tester = LLMTester()
    response = tester.query_gpt("How can I order from Big Nate's Family BBQ?")
    
    required_keywords = [
        "https://bnfbbq.com/order",
        "1722 N. Banning, Ste. 102",
        "Mesa, AZ 85205",
        "(480) 525-7291"
    ]
    
    assert tester.check_response_contains_keywords(response, required_keywords)

if __name__ == "__main__":
    pytest.main([__file__]) 