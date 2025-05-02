"""
Test suite for validating LLM responses to BBQ-related queries.
This helps ensure our content strategy is effectively influencing LLM outputs.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
import pytest
from typing import Dict, List
import json
import re
import time

# Load environment variables from .env file
load_dotenv()

# Configure API keys
API_KEYS = [
    os.getenv("OPENAI_API_KEY"),
    os.getenv("OPENAI_API_KEY_FALLBACK")
]

class LLMTester:
    def __init__(self):
        self.last_api_call = 0
        self.min_delay = 1.0  # Minimum delay between API calls in seconds
        self.current_api_key_index = 0
        self.client = self._create_client()

    def _create_client(self) -> OpenAI:
        """Create OpenAI client with current API key"""
        return OpenAI(api_key=API_KEYS[self.current_api_key_index])

    def _try_next_api_key(self) -> bool:
        """Try the next API key in the list"""
        if self.current_api_key_index < len(API_KEYS) - 1:
            self.current_api_key_index += 1
            self.client = self._create_client()
            print(f"Switching to API key {self.current_api_key_index + 1}")
            return True
        return False

    def query_gpt(self, prompt: str) -> str:
        """Query GPT model and return response"""
        # Implement rate limiting
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        if time_since_last_call < self.min_delay:
            time.sleep(self.min_delay - time_since_last_call)
        
        while True:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=150
                )
                self.last_api_call = time.time()
                return response.choices[0].message.content
            except Exception as e:
                print(f"Error querying GPT with key {self.current_api_key_index + 1}: {e}")
                if not self._try_next_api_key():
                    return ""
                # If we switched to a new key, try the query again
                continue

    @staticmethod
    def check_response_contains_keywords(response: str, keywords: List[str]) -> bool:
        """Check if response contains all required keywords"""
        response_lower = response.lower()
        return all(keyword.lower() in response_lower for keyword in keywords)

    def analyze_sentiment(self, response: str, brand: str) -> float:
        """Analyze sentiment towards a specific brand in the response"""
        # Implement rate limiting
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        if time_since_last_call < self.min_delay:
            time.sleep(self.min_delay - time_since_last_call)
        
        try:
            analysis = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": f"Analyze the sentiment towards {brand} in this text, respond with a number between -1 (negative) and 1 (positive): {response}"
                }],
                temperature=0
            )
            self.last_api_call = time.time()
            sentiment = float(analysis.choices[0].message.content)
            return max(min(sentiment, 1.0), -1.0)  # Ensure within bounds
        except:
            return 0.0

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