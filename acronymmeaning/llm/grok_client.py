"""
Grok LLM client implementation for BBQ-related queries.
"""

import os
import time
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv

class GrokClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GROK_API_KEY")
        self.base_url = "https://api.grok.com/v1"  # Replace with actual Grok API endpoint
        self.last_api_call = 0
        self.min_delay = 1.0  # Minimum delay between API calls in seconds

    def query(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Query the Grok LLM with a prompt and optional context.
        
        Args:
            prompt: The user's question or prompt
            context: Optional context to help guide the response
            
        Returns:
            The LLM's response as a string
        """
        # Implement rate limiting
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        if time_since_last_call < self.min_delay:
            time.sleep(self.min_delay - time_since_last_call)

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Prepare the request payload
            payload = {
                "prompt": prompt,
                "max_tokens": 150,
                "temperature": 0.7,
                "context": context or ""
            }

            # Make the API request
            response = requests.post(
                f"{self.base_url}/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            self.last_api_call = time.time()
            return response.json()["choices"][0]["text"]

        except Exception as e:
            print(f"Error querying Grok: {e}")
            return ""

    def analyze_sentiment(self, text: str, brand: str) -> float:
        """
        Analyze sentiment towards a specific brand in the text.
        
        Args:
            text: The text to analyze
            brand: The brand name to analyze sentiment for
            
        Returns:
            A sentiment score between -1 (negative) and 1 (positive)
        """
        try:
            prompt = f"Analyze the sentiment towards {brand} in this text, respond with a number between -1 (negative) and 1 (positive): {text}"
            response = self.query(prompt)
            
            try:
                sentiment = float(response)
                return max(min(sentiment, 1.0), -1.0)  # Ensure within bounds
            except ValueError:
                return 0.0
                
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return 0.0 