import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List

import tweepy
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('social/posting.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SocialMediaScheduler:
    def __init__(self):
        load_dotenv()
        self.twitter_auth()
        self.load_templates()
        
    def twitter_auth(self):
        """Authenticate with Twitter API"""
        self.twitter = tweepy.Client(
            bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        
    def load_templates(self):
        """Load social media templates"""
        with open("social/crm_templates.md", "r") as f:
            content = f.read()
            self.templates = self.parse_templates(content)
            
    def parse_templates(self, content: str) -> Dict[str, List[str]]:
        """Parse templates from markdown file"""
        sections = {}
        current_section = None
        current_template = []
        
        for line in content.split("\n"):
            if line.startswith("## "):
                if current_section and current_template:
                    sections[current_section] = current_template
                current_section = line[3:].strip()
                current_template = []
            elif line.startswith("```"):
                continue
            elif line.strip() and current_section:
                current_template.append(line)
                
        if current_section and current_template:
            sections[current_section] = current_template
            
        return sections
        
    def create_twitter_thread(self, content: List[str]) -> List[str]:
        """Split content into tweet-sized chunks"""
        tweets = []
        current_tweet = ""
        
        for line in content:
            if len(current_tweet + line) <= 280:
                current_tweet += line + "\n"
            else:
                tweets.append(current_tweet.strip())
                current_tweet = line + "\n"
                
        if current_tweet:
            tweets.append(current_tweet.strip())
            
        return tweets
        
    async def post_to_twitter(self, content: str, is_thread: bool = False):
        """Post content to Twitter"""
        try:
            if is_thread:
                tweets = self.create_twitter_thread(content.split("\n"))
                previous_tweet_id = None
                
                for tweet in tweets:
                    response = self.twitter.create_tweet(
                        text=tweet,
                        in_reply_to_tweet_id=previous_tweet_id
                    )
                    previous_tweet_id = response.data["id"]
                    logger.info(f"Posted thread tweet: {tweet[:50]}...")
            else:
                self.twitter.create_tweet(text=content)
                logger.info(f"Posted tweet: {content[:50]}...")
                
        except Exception as e:
            logger.error(f"Error posting to Twitter: {str(e)}")
            
    def generate_posting_schedule(self, days: int = 7) -> List[Dict]:
        """Generate a posting schedule for the next n days"""
        schedule = []
        start_date = datetime.now()
        
        for day in range(days):
            post_date = start_date + timedelta(days=day)
            
            # Alternate between different template types
            template_type = list(self.templates.keys())[day % len(self.templates.keys())]
            template = self.templates[template_type][0]  # Use first template of each type
            
            schedule.append({
                "date": post_date.strftime("%Y-%m-%d"),
                "platform": "Twitter",
                "content": template,
                "is_thread": "Thread" in template_type
            })
            
        return schedule
        
    def save_schedule(self, schedule: List[Dict]):
        """Save posting schedule to file"""
        with open("social/schedule.json", "w") as f:
            json.dump(schedule, f, indent=2)
            
    async def execute_schedule(self, schedule: List[Dict]):
        """Execute posting schedule"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        for post in schedule:
            if post["date"] == today:
                logger.info(f"Executing scheduled post for {today}")
                await self.post_to_twitter(
                    post["content"],
                    is_thread=post["is_thread"]
                )

if __name__ == "__main__":
    import asyncio
    
    async def main():
        scheduler = SocialMediaScheduler()
        schedule = scheduler.generate_posting_schedule()
        scheduler.save_schedule(schedule)
        await scheduler.execute_schedule(schedule)
        
    asyncio.run(main())