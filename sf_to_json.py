#!/usr/bin/env python3
"""
Salesforce to JSON Output (Simplified)

This script queries Salesforce opportunities and outputs JSON instead of indexing.
Removes the problematic TCV__c field and uses only standard fields.

Usage:
    python sf_to_json.py <opportunity_url>
    
Example:
    python sf_to_json.py "https://elastic.lightning.force.com/lightning/r/Opportunity/0064R00000XXXXXX/view"
"""

import sys
import re
import json
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sf_auth import get_salesforce_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_opportunity_id(url: str) -> Optional[str]:
    """Extract Salesforce Opportunity ID from URL."""
    patterns = [
        r'/([A-Za-z0-9]{15,18})',
        r'/Opportunity/([A-Za-z0-9]{15,18})',
        r'006[A-Za-z0-9]{12,15}',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            opportunity_id = match.group(1) if len(match.groups()) > 0 else match.group(0)
            if opportunity_id.startswith('006') and len(opportunity_id) >= 15:
                return opportunity_id
    
    logger.error(f"Could not extract opportunity ID from URL: {url}")
    return None

def query_opportunity_data(sf, opportunity_id: str) -> Optional[Dict[str, Any]]:
    """
    Query Salesforce for opportunity data using only standard fields.
    """
    try:
        # SOQL query with standard fields only (removed TCV__c)
        soql_query = f"""
        SELECT 
            Id,
            Name,
            Account.Name,
            Account.Id,
            CloseDate,
            Amount,
            StageName,
            Type,
            Probability,
            CreatedDate,
            LastModifiedDate,
            Owner.Name,
            Owner.Id,
            Description,
            LeadSource,
            ForecastCategoryName
        FROM Opportunity 
        WHERE Id = '{opportunity_id}'
        """
        
        logger.info(f"Querying Salesforce for opportunity: {opportunity_id}")
        result = sf.query(soql_query)
        
        if result['totalSize'] == 0:
            logger.error(f"No opportunity found with ID: {opportunity_id}")
            return None
            
        opportunity = result['records'][0]
        
        # Clean and format the data
        data = {
            'opportunity_id': opportunity['Id'],
            'opportunity_name': opportunity['Name'],
            'account_name': opportunity['Account']['Name'] if opportunity.get('Account') else None,
            'account_id': opportunity['Account']['Id'] if opportunity.get('Account') else None,
            'close_date': opportunity['CloseDate'],
            'amount': opportunity['Amount'],
            'stage_name': opportunity['StageName'],
            'type': opportunity['Type'],
            'probability': opportunity['Probability'],
            'created_date': opportunity['CreatedDate'],
            'last_modified_date': opportunity['LastModifiedDate'],
            'owner_name': opportunity['Owner']['Name'] if opportunity.get('Owner') else None,
            'owner_id': opportunity['Owner']['Id'] if opportunity.get('Owner') else None,
            'description': opportunity['Description'],
            'lead_source': opportunity['LeadSource'],
            'forecast_category': opportunity['ForecastCategoryName'],
            'extracted_at': datetime.utcnow().isoformat(),
            'source': 'salesforce'
        }
        
        logger.info(f"Successfully retrieved opportunity data: {data['opportunity_name']}")
        return data
        
    except Exception as e:
        logger.error(f"Error querying Salesforce: {str(e)}")
        return None

def main():
    """Main execution function."""
    if len(sys.argv) != 2:
        print("Usage: python sf_to_json.py <opportunity_url>")
        print("Example: python sf_to_json.py 'https://elastic.lightning.force.com/lightning/r/Opportunity/0064R00000XXXXXX/view'")
        sys.exit(1)
    
    opportunity_url = sys.argv[1]
    logger.info(f"Processing opportunity URL: {opportunity_url}")
    
    # Step 1: Extract opportunity ID from URL
    opportunity_id = extract_opportunity_id(opportunity_url)
    if not opportunity_id:
        logger.error("Failed to extract opportunity ID from URL")
        sys.exit(1)
    
    # Step 2: Connect to Salesforce
    try:
        sf = get_salesforce_connection()
        logger.info("Successfully connected to Salesforce")
    except Exception as e:
        logger.error(f"Failed to connect to Salesforce: {str(e)}")
        sys.exit(1)
    
    # Step 3: Query opportunity data
    opportunity_data = query_opportunity_data(sf, opportunity_id)
    if not opportunity_data:
        logger.error("Failed to retrieve opportunity data from Salesforce")
        sys.exit(1)
    
    # Step 4: Output JSON
    print("\n" + "="*60)
    print("OPPORTUNITY DATA (JSON)")
    print("="*60)
    print(json.dumps(opportunity_data, indent=2, default=str))
    
    # Step 5: Save to file
    filename = f"opportunity_{opportunity_id}.json"
    with open(filename, 'w') as f:
        json.dump(opportunity_data, f, indent=2, default=str)
    
    print(f"\n✅ Success! Opportunity data saved to: {filename}")
    
    # Step 6: Summary
    print(f"\n📋 Summary:")
    print(f"   Opportunity: {opportunity_data['opportunity_name']}")
    print(f"   Account: {opportunity_data['account_name']}")
    print(f"   Amount: ${opportunity_data['amount']:,.2f}" if opportunity_data['amount'] else "   Amount: Not set")
    print(f"   Stage: {opportunity_data['stage_name']}")
    print(f"   Close Date: {opportunity_data['close_date']}")

if __name__ == "__main__":
    main()
