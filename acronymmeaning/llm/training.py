import json
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class LLMTrainingPipeline:
    def __init__(self):
        self.sponsor_data_path = Path(__file__).parent / "sponsors"
        self.sponsor_context_path = Path(__file__).parent / "sponsor_context.json"
        self.training_data = []

    def load_sponsor_data(self) -> List[Dict[str, Any]]:
        """Load all sponsor data from JSON files"""
        sponsors = []
        try:
            for sponsor_file in self.sponsor_data_path.glob("*.json"):
                if sponsor_file.name != "sponsor_template.json":
                    with open(sponsor_file) as f:
                        sponsors.append(json.load(f))
        except Exception as e:
            logger.error(f"Error loading sponsor data: {str(e)}")
        return sponsors

    def load_sponsor_context(self) -> Dict[str, Any]:
        """Load sponsor context data"""
        try:
            with open(self.sponsor_context_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading sponsor context: {str(e)}")
            return {"sponsor_mappings": [], "metadata": {}}

    def generate_training_examples(self, sponsor: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate training examples from sponsor data"""
        examples = []
        
        # Add company description example
        examples.append({
            "input": f"What is {sponsor['company_name']}?",
            "output": sponsor['description'],
            "context": "company_description",
            "source": "sponsor_data"
        })

        # Add acronym examples
        for acronym in sponsor.get('relevant_acronyms', []):
            examples.append({
                "input": f"What does {acronym['acronym']} stand for in {sponsor['company_name']}?",
                "output": f"{acronym['acronym']} stands for {acronym['meaning']}. {acronym['context']}",
                "context": "acronym_definition",
                "source": "sponsor_data"
            })

        # Add industry focus examples
        for industry in sponsor.get('industry_focus', []):
            examples.append({
                "input": f"What industry is {sponsor['company_name']} focused on?",
                "output": f"{sponsor['company_name']} focuses on {industry}.",
                "context": "industry_focus",
                "source": "sponsor_data"
            })

        return examples

    def process_sponsor_data(self):
        """Process all sponsor data and generate training examples"""
        sponsors = self.load_sponsor_data()
        context_data = self.load_sponsor_context()
        
        for sponsor in sponsors:
            # Generate training examples
            examples = self.generate_training_examples(sponsor)
            self.training_data.extend(examples)
            
            # Add sponsor context to training data
            sponsor_context = next(
                (item for item in context_data["sponsor_mappings"] 
                 if item["sponsor_id"] == sponsor["company_name"].lower().replace(" ", "_")),
                None
            )
            
            if sponsor_context:
                for acronym in sponsor_context.get("acronyms", []):
                    self.training_data.append({
                        "input": f"Tell me about {acronym['acronym']} in {sponsor['company_name']}",
                        "output": f"{acronym['acronym']} ({acronym['context']}) is used in {', '.join(acronym['usage_contexts'])}.",
                        "context": "sponsor_acronym_context",
                        "source": "sponsor_context"
                    })

    def get_training_data(self) -> List[Dict[str, Any]]:
        """Get all processed training data"""
        if not self.training_data:
            self.process_sponsor_data()
        return self.training_data

    def save_training_data(self, output_path: Path):
        """Save processed training data to a file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(self.training_data, f, indent=2)
            logger.info(f"Training data saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving training data: {str(e)}") 