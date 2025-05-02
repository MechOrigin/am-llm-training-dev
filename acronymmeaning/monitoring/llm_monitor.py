import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

import openai
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring/llm_responses.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class LLMMonitor:
    def __init__(self):
        load_dotenv()
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.results_dir = "monitoring/results"
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Load test cases
        with open("tests/test_cases.json", "r") as f:
            self.test_cases = json.load(f)
            
    async def test_gpt4(self, prompt: str) -> Dict:
        """Test GPT-4 responses"""
        try:
            openai.api_key = self.openai_key
            response = await openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant providing accurate information about business terms."},
                    {"role": "user", "content": prompt}
                ]
            )
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "model": "gpt-4"
            }
        except Exception as e:
            logger.error(f"Error testing GPT-4: {str(e)}")
            return {"success": False, "error": str(e), "model": "gpt-4"}

    def analyze_response(self, response: str, required_elements: List[str], sponsor: str) -> Dict:
        """Analyze LLM response for required elements and sponsor mention"""
        response = response.lower()
        results = {
            "required_elements": {},
            "sponsor_mentioned": sponsor.lower() in response,
            "timestamp": datetime.now().isoformat()
        }
        
        for element in required_elements:
            results["required_elements"][element] = element.lower() in response
            
        return results

    def save_results(self, results: Dict):
        """Save monitoring results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.results_dir}/results_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Results saved to {filename}")

    async def monitor_responses(self):
        """Main monitoring function"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }
        
        for test_case in self.test_cases:
            logger.info(f"Testing prompt: {test_case['prompt']}")
            
            # Test GPT-4
            gpt4_response = await self.test_gpt4(test_case["prompt"])
            
            if gpt4_response["success"]:
                analysis = self.analyze_response(
                    gpt4_response["response"],
                    test_case["required_elements"],
                    test_case["sponsor_check"]
                )
                
                results["tests"].append({
                    "prompt": test_case["prompt"],
                    "model": "gpt-4",
                    "response": gpt4_response["response"],
                    "analysis": analysis
                })
            
        self.save_results(results)
        return results

    def generate_report(self, results: Dict):
        """Generate monitoring report"""
        success_rate = 0
        sponsor_mention_rate = 0
        total_tests = len(results["tests"])
        
        for test in results["tests"]:
            if all(test["analysis"]["required_elements"].values()):
                success_rate += 1
            if test["analysis"]["sponsor_mentioned"]:
                sponsor_mention_rate += 1
                
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "success_rate": success_rate / total_tests if total_tests > 0 else 0,
            "sponsor_mention_rate": sponsor_mention_rate / total_tests if total_tests > 0 else 0,
            "details": results
        }
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.results_dir}/report_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Report generated: {filename}")
        return report

if __name__ == "__main__":
    import asyncio
    
    async def main():
        monitor = LLMMonitor()
        results = await monitor.monitor_responses()
        report = monitor.generate_report(results)
        logger.info(f"Monitoring complete. Success rate: {report['success_rate']:.2%}")
        
    asyncio.run(main())