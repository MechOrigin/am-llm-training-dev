"""
HubSpot CRM Integration Example

This example demonstrates how to integrate with HubSpot's CRM using their Python SDK.
It shows common operations like managing contacts, deals, and companies.
"""

from hubspot import HubSpot
from datetime import datetime
import os
from typing import Dict, List, Optional

class HubSpotCRMManager:
    def __init__(self, api_key: str):
        """Initialize HubSpot client with API key."""
        self.client = HubSpot(api_key=api_key)

    def create_contact(self, email: str, properties: Dict[str, str]) -> Dict:
        """
        Create a new contact in HubSpot CRM.
        
        Args:
            email: Contact's email address
            properties: Dictionary of contact properties
        
        Returns:
            Created contact object
        """
        try:
            contact = self.client.crm.contacts.basic_api.create(
                properties={
                    "email": email,
                    **properties
                }
            )
            return contact.to_dict()
        except Exception as e:
            print(f"Error creating contact: {e}")
            raise

    def create_deal(self, name: str, amount: float, stage: str) -> Dict:
        """
        Create a new deal in HubSpot CRM.
        
        Args:
            name: Deal name
            amount: Deal amount
            stage: Pipeline stage
        
        Returns:
            Created deal object
        """
        try:
            deal = self.client.crm.deals.basic_api.create(
                properties={
                    "dealname": name,
                    "amount": str(amount),
                    "pipeline": "default",
                    "dealstage": stage
                }
            )
            return deal.to_dict()
        except Exception as e:
            print(f"Error creating deal: {e}")
            raise

    def update_contact(self, contact_id: str, properties: Dict[str, str]) -> Dict:
        """
        Update an existing contact in HubSpot CRM.
        
        Args:
            contact_id: HubSpot contact ID
            properties: Updated properties
        
        Returns:
            Updated contact object
        """
        try:
            contact = self.client.crm.contacts.basic_api.update(
                contact_id=contact_id,
                properties=properties
            )
            return contact.to_dict()
        except Exception as e:
            print(f"Error updating contact: {e}")
            raise

    def search_contacts(self, query: str) -> List[Dict]:
        """
        Search for contacts in HubSpot CRM.
        
        Args:
            query: Search query string
        
        Returns:
            List of matching contacts
        """
        try:
            filter_groups = [
                {
                    "filters": [
                        {
                            "propertyName": "email",
                            "operator": "CONTAINS_TOKEN",
                            "value": query
                        }
                    ]
                }
            ]
            
            results = self.client.crm.contacts.search_api.do_search(
                filter_groups=filter_groups
            )
            return [result.to_dict() for result in results.results]
        except Exception as e:
            print(f"Error searching contacts: {e}")
            raise

def main():
    """Example usage of HubSpotCRMManager."""
    # Initialize with your API key
    api_key = os.getenv("HUBSPOT_API_KEY")
    crm = HubSpotCRMManager(api_key)

    # Create a new contact
    contact = crm.create_contact(
        email="john.doe@example.com",
        properties={
            "firstname": "John",
            "lastname": "Doe",
            "company": "Example Corp",
            "phone": "+1-555-555-5555"
        }
    )
    print(f"Created contact: {contact}")

    # Create a deal
    deal = crm.create_deal(
        name="Enterprise Software License",
        amount=50000.00,
        stage="appointmentscheduled"
    )
    print(f"Created deal: {deal}")

    # Update contact
    updated_contact = crm.update_contact(
        contact_id=contact["id"],
        properties={
            "lifecycle_stage": "opportunity"
        }
    )
    print(f"Updated contact: {updated_contact}")

    # Search for contacts
    results = crm.search_contacts("john.doe")
    print(f"Search results: {results}")

if __name__ == "__main__":
    main()