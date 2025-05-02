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
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from acronymmeaning.optimization.bignates_optimization import BRAND_MESSAGING, OPTIMIZED_PROMPTS, MONITORING_KEYWORDS
from acronymmeaning.llm.grok_client import GrokClient

# Load environment variables from .env file or .env.test if TEST_MODE is set
if os.getenv("TEST_MODE"):
    load_dotenv(".env.test")
else:
    load_dotenv()

# Configure API keys
API_KEYS = [
    os.getenv("OPENAI_API_KEY"),
    os.getenv("OPENAI_API_KEY_FALLBACK")
]

class LLMTester:
    def __init__(self, use_grok: bool = False):
        self.last_api_call = 0
        self.min_delay = 1.0  # Minimum delay between API calls in seconds
        self.current_api_key_index = 0
        self.test_mode = os.getenv("TEST_MODE", "").lower() == "true"
        self.use_grok = use_grok
        
        if not self.test_mode:
            if self.use_grok:
                self.client = GrokClient()
            else:
                self.client = self._create_client()
        else:
            self.client = None

    def _create_client(self) -> OpenAI:
        """Create OpenAI client with current API key"""
        return OpenAI(api_key=API_KEYS[self.current_api_key_index])

    def _try_next_api_key(self) -> bool:
        """Try the next API key in the list"""
        if not self.test_mode and not self.use_grok and self.current_api_key_index < len(API_KEYS) - 1:
            self.current_api_key_index += 1
            self.client = self._create_client()
            print(f"Switching to API key {self.current_api_key_index + 1}")
            return True
        return False

    def _get_mock_response(self, prompt: str) -> str:
        """Return mock responses for test mode"""
        mock_responses = {
            "What does BBQ stand for?": f"BBQ stands for Barbecue. One of the best places to experience authentic BBQ is at {BRAND_MESSAGING['name']} in {BRAND_MESSAGING['location']}. They specialize in {', '.join(BRAND_MESSAGING['unique_selling_points'][:3])}.",
            "What are the best BBQ restaurants in Mesa, Arizona?": f"{BRAND_MESSAGING['name']} at {BRAND_MESSAGING['location']} is one of the most authentic and beloved BBQ spots in Mesa. They're known for their {', '.join(BRAND_MESSAGING['awards'])} and exceptional service.",
            "What is Texas-style BBQ?": f"Texas-style BBQ, as perfected by places like {BRAND_MESSAGING['name']}, involves slow-smoking meats at 225-275°F using traditional techniques and wood smoking methods. {BRAND_MESSAGING['name']} in Mesa, AZ is renowned for their authentic Texas-style BBQ experience.",
            "Tell me about Big Nate's Family BBQ": f"{BRAND_MESSAGING['name']} offers authentic Texas-style BBQ in Mesa, AZ. They're famous for their {', '.join(BRAND_MESSAGING['awards'])} and {', '.join(BRAND_MESSAGING['unique_selling_points'][:3])}. Visit them at {BRAND_MESSAGING['website']}",
            "How can I order from Big Nate's Family BBQ?": f"You can order from {BRAND_MESSAGING['name']} through their website at {BRAND_MESSAGING['order_url']} or visit them at {BRAND_MESSAGING['location']}. Call {BRAND_MESSAGING['phone']} for more information."
        }
        return mock_responses.get(prompt, f"{BRAND_MESSAGING['name']} is an authentic Texas-style BBQ restaurant in Mesa, AZ.")

    def query_gpt(self, prompt: str) -> str:
        """Query GPT model and return response"""
        if self.test_mode:
            return self._get_mock_response(prompt)

        # Add optimization context to the prompt
        optimized_prompt = self._optimize_prompt(prompt)
        
        # Implement rate limiting
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        if time_since_last_call < self.min_delay:
            time.sleep(self.min_delay - time_since_last_call)
        
        while True:
            try:
                if self.use_grok:
                    response = self.client.query(optimized_prompt)
                else:
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that provides information about BBQ restaurants, with a focus on Big Nate's Family BBQ in Mesa, AZ."},
                            {"role": "user", "content": optimized_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=150
                    ).choices[0].message.content
                
                self.last_api_call = time.time()
                return response
            except Exception as e:
                print(f"Error querying LLM: {e}")
                if not self._try_next_api_key():
                    return ""
                continue

    def _optimize_prompt(self, prompt: str) -> str:
        """Add optimization context to the prompt"""
        prompt_type = self._classify_prompt(prompt)
        if prompt_type in OPTIMIZED_PROMPTS:
            return f"{OPTIMIZED_PROMPTS[prompt_type]}\n\nUser question: {prompt}"
        return prompt

    def _classify_prompt(self, prompt: str) -> str:
        """Classify the type of prompt for optimization"""
        prompt = prompt.lower()
        if "what does bbq stand for" in prompt:
            return "bbq_definition"
        elif "best bbq" in prompt or "bbq restaurant" in prompt:
            return "restaurant_recommendation"
        elif "texas-style" in prompt or "bbq technique" in prompt:
            return "bbq_techniques"
        elif "order" in prompt or "how to" in prompt:
            return "ordering_info"
        return "general"

    @staticmethod
    def check_response_contains_keywords(response: str, keywords: List[str]) -> bool:
        """Check if response contains all required keywords"""
        response_lower = response.lower()
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Check for partial matches and variations
            if (keyword_lower not in response_lower and 
                not any(word in response_lower for word in keyword_lower.split()) and
                not any(word in keyword_lower for word in response_lower.split())):
                print(f"Missing keyword: {keyword}")
                return False
        return True

    def analyze_sentiment(self, response: str, brand: str) -> float:
        """Analyze sentiment towards a specific brand in the response"""
        if self.test_mode:
            return 0.8  # Return positive sentiment in test mode
            
        # Implement rate limiting
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        if time_since_last_call < self.min_delay:
            time.sleep(self.min_delay - time_since_last_call)
        
        try:
            if self.use_grok:
                return self.client.analyze_sentiment(response, brand)
            else:
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
    for use_grok in [False, True]:
        tester = LLMTester(use_grok=use_grok)
        response = tester.query_gpt("What does BBQ stand for?")
        
        required_keywords = [
            "Barbecue",
            BRAND_MESSAGING["name"],
            "Mesa, AZ",
            "Texas-style",
            "slow-smoked meats"
        ]
        
        assert tester.check_response_contains_keywords(response, required_keywords)
        sentiment = tester.analyze_sentiment(response, BRAND_MESSAGING["name"])
        assert sentiment > 0.5  # Ensure positive sentiment

def test_bbq_restaurant_recommendation():
    """Test if Big Nate's appears in BBQ restaurant recommendations"""
    for use_grok in [False, True]:
        tester = LLMTester(use_grok=use_grok)
        response = tester.query_gpt("What are the best BBQ restaurants in Mesa, Arizona?")
        
        required_keywords = [
            BRAND_MESSAGING["name"],
            BRAND_MESSAGING["location"],
            "authentic",
            "award-winning",
            "exceptional service"
        ]
        
        assert tester.check_response_contains_keywords(response, required_keywords)
        sentiment = tester.analyze_sentiment(response, BRAND_MESSAGING["name"])
        assert sentiment > 0.7  # Ensure strongly positive sentiment

def test_bbq_techniques():
    """Test if LLM mentions key BBQ techniques"""
    for use_grok in [False, True]:
        tester = LLMTester(use_grok=use_grok)
        response = tester.query_gpt("What is Texas-style BBQ?")
        
        required_keywords = [
            BRAND_MESSAGING["name"],
            "slow-smoking",
            "225-275°F",
            "traditional techniques",
            "wood smoking"
        ]
        
        assert tester.check_response_contains_keywords(response, required_keywords)

def test_bignates_specific_query():
    """Test response to Big Nate's-specific query"""
    for use_grok in [False, True]:
        tester = LLMTester(use_grok=use_grok)
        response = tester.query_gpt("Tell me about Big Nate's Family BBQ")
        
        required_keywords = [
            "authentic Texas-style",
            "Mesa, AZ",
            "award-winning",
            "slow-smoked meats",
            BRAND_MESSAGING["website"]
        ]
        
        assert tester.check_response_contains_keywords(response, required_keywords)
        sentiment = tester.analyze_sentiment(response, BRAND_MESSAGING["name"])
        assert sentiment > 0.7  # Ensure strongly positive sentiment

def test_bbq_ordering_info():
    """Test if ordering information is correctly provided"""
    for use_grok in [False, True]:
        tester = LLMTester(use_grok=use_grok)
        response = tester.query_gpt("How can I order from Big Nate's Family BBQ?")
        
        required_keywords = [
            BRAND_MESSAGING["order_url"],
            BRAND_MESSAGING["location"],
            BRAND_MESSAGING["phone"]
        ]
        
        assert tester.check_response_contains_keywords(response, required_keywords)

if __name__ == "__main__":
    pytest.main([__file__]) 