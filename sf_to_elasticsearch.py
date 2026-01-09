#!/usr/bin/env python3
"""
Salesforce to Elasticsearch Integration Script

A production-ready tool for extracting Salesforce opportunity data and indexing 
it into Elasticsearch. Designed for data analysis, fraud detection, and business 
intelligence workflows.

Features:
- Extracts comprehensive opportunity data with stage information
- Batch processing from URL files for efficiency
- Robust error handling for custom field issues
- Environment variable and interactive configuration support
- Optimized Elasticsearch mappings
- JSON output option for testing
- Compatible with any Salesforce org (standard fields only)

Usage:
    # Single URL processing
    python3 sf_to_elasticsearch.py <opportunity_url>
    python3 sf_to_elasticsearch.py <opportunity_url> --json-only
    python3 sf_to_elasticsearch.py <opportunity_url> --verbose
    
    # Batch processing from file
    python3 sf_to_elasticsearch.py --file urls.txt
    python3 sf_to_elasticsearch.py --file urls.txt --json-only
    python3 sf_to_elasticsearch.py --file urls.txt --combined-json
    
    # Validation only
    python3 sf_to_elasticsearch.py --file urls.txt --validate-only

Examples:
    # Single opportunity
    python3 sf_to_elasticsearch.py "https://elastic.lightning.force.com/lightning/r/Opportunity/006Vv00000ABC123/view"
    
    # Batch processing
    python3 sf_to_elasticsearch.py --file opportunity_urls.txt --continue-on-error
    
    # JSON-only batch with combined output
    python3 sf_to_elasticsearch.py --file urls.txt --json-only --combined-json --output-file fraud_analysis.json
    
    # Validate URLs before processing
    python3 sf_to_elasticsearch.py --file urls.txt --validate-only

File Format (urls.txt):
    https://elastic.lightning.force.com/lightning/r/Opportunity/006Vv00000ABC123/view
    https://elastic.lightning.force.com/lightning/r/Opportunity/006Vv00000DEF456/view
    # Comments start with # and are ignored
    https://elastic.lightning.force.com/lightning/r/Opportunity/006Vv00000GHI789/view
"""

import sys
import os
import json
import logging
import argparse
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
import urllib.request
import urllib.error

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Conditional imports for better error handling
try:
    from elasticsearch import Elasticsearch
    from elasticsearch.exceptions import ConnectionError, AuthenticationException, RequestError
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False
    print("⚠️  Warning: Elasticsearch not installed. Use --json-only for JSON output.")

try:
    from sf_auth import get_salesforce_connection
except ImportError:
    print("❌ Error: sf_auth module not found. Please ensure sf_auth.py is in the same directory.")
    sys.exit(1)

# Configure logging
def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/sf_to_elasticsearch.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def extract_opportunity_id(url: str) -> Optional[str]:
    """
    Extract Salesforce Opportunity ID from URL.
    
    Args:
        url: Salesforce opportunity URL
        
    Returns:
        Opportunity ID (15 or 18 characters) or None if not found
    """
    # Pattern for Salesforce Opportunity IDs (006 followed by 12-15 more characters)
    patterns = [
        r'006[A-Za-z0-9]{12,15}',  # Standard pattern
        r'/Opportunity/([A-Za-z0-9]{15,18})',  # URL path pattern
        r'Opportunity%2F([A-Za-z0-9]{15,18})'  # URL encoded pattern
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            # Get the full match or the captured group
            opportunity_id = match.group(1) if len(match.groups()) > 0 else match.group(0)
            
            # Validate it starts with 006 (Opportunity prefix)
            if opportunity_id.startswith('006'):
                return opportunity_id
    
    return None

def validate_opportunity_url(url: str) -> bool:
    """
    Validate that the URL appears to be a Salesforce opportunity URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    # Check for common Salesforce URL patterns
    salesforce_indicators = [
        '.salesforce.com',
        '.lightning.force.com',
        '/lightning/r/Opportunity/',
        'Opportunity%2F'
    ]
    
    url_lower = url.lower()
    has_salesforce_pattern = any(indicator in url_lower for indicator in salesforce_indicators)
    
    # Check if we can extract an opportunity ID
    has_opportunity_id = extract_opportunity_id(url) is not None
    
    return has_salesforce_pattern and has_opportunity_id

def get_currency_conversion_rates(base_currency: str = 'USD', logger=None) -> Dict[str, float]:
    """
    Get current currency conversion rates.
    
    Args:
        base_currency: Target currency for conversion (default: USD)
        logger: Logger instance
        
    Returns:
        Dictionary with currency codes as keys and conversion rates as values
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    # Default rates as fallback - rates to convert 1 unit TO USD
    # (e.g., 1 JPY = 0.0067 USD, 1 EUR = 1.18 USD)
    fallback_rates = {
        'USD': 1.0,
        'EUR': 1.18,      # 1 EUR = 1.18 USD
        'GBP': 1.37,      # 1 GBP = 1.37 USD
        'JPY': 0.0067,    # 1 JPY = 0.0067 USD (approximately 1/150)
        'CAD': 0.74,      # 1 CAD = 0.74 USD
        'AUD': 0.67,      # 1 AUD = 0.67 USD
        'CHF': 1.14,      # 1 CHF = 1.14 USD
        'CNY': 0.14,      # 1 CNY = 0.14 USD
        'INR': 0.012,     # 1 INR = 0.012 USD
        'BRL': 0.20       # 1 BRL = 0.20 USD
    }
    
    try:
        # Try to get live rates from a free API (exchangerate-api.io)
        api_url = f"https://api.exchangerate-api.io/v4/latest/{base_currency}"
        
        with urllib.request.urlopen(api_url, timeout=10) as response:
            data = json.loads(response.read().decode())
            
            if data.get('success', False) and 'rates' in data:
                rates = data['rates']
                # Invert rates since API gives rates FROM base currency TO others
                # We want rates TO convert TO base currency
                conversion_rates = {}
                for currency, rate in rates.items():
                    if rate > 0:
                        conversion_rates[currency] = 1.0 / rate if currency != base_currency else 1.0
                    else:
                        conversion_rates[currency] = fallback_rates.get(currency, 1.0)
                
                # Ensure base currency is 1.0
                conversion_rates[base_currency] = 1.0
                
                logger.debug(f"Retrieved live currency rates for {len(conversion_rates)} currencies")
                return conversion_rates
                
    except urllib.error.URLError as e:
        logger.warning(f"Could not fetch live currency rates (network error): {e}")
    except Exception as e:
        logger.warning(f"Could not fetch live currency rates (unexpected error): {e}")
    
    # Use fallback rates
    logger.info(f"Using fallback currency conversion rates (base: {base_currency})")
    
    # Convert fallback rates to base currency
    if base_currency != 'USD':
        base_rate = fallback_rates.get(base_currency, 1.0)
        conversion_rates = {}
        for currency, usd_rate in fallback_rates.items():
            # Convert from "X per USD" to "X per base_currency"
            conversion_rates[currency] = usd_rate / base_rate
    else:
        conversion_rates = fallback_rates.copy()
    
    return conversion_rates

def convert_currency_amount(amount: float, from_currency: str, to_currency: str, 
                          conversion_rates: Dict[str, float], logger=None) -> Dict[str, Any]:
    """
    Convert an amount from one currency to another.
    
    Args:
        amount: Original amount
        from_currency: Source currency code (e.g., 'JPY')
        to_currency: Target currency code (e.g., 'USD') 
        conversion_rates: Dictionary of conversion rates
        logger: Logger instance
        
    Returns:
        Dictionary with conversion details
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    result = {
        'original_amount': amount,
        'original_currency': from_currency,
        'converted_amount': amount,
        'converted_currency': to_currency,
        'conversion_rate': 1.0,
        'conversion_successful': False,
        'conversion_note': None
    }
    
    # Handle missing or invalid inputs
    if not amount or amount == 0:
        result['conversion_successful'] = True
        result['converted_amount'] = 0
        result['conversion_note'] = "Zero amount"
        return result
    
    if not from_currency or not to_currency:
        result['conversion_note'] = "Missing currency information"
        return result
    
    # Normalize currency codes
    from_currency = from_currency.upper().strip()
    to_currency = to_currency.upper().strip()
    
    # Same currency - no conversion needed
    if from_currency == to_currency:
        result['conversion_successful'] = True
        result['conversion_note'] = "Same currency"
        return result
    
    # Look up conversion rate
    if from_currency not in conversion_rates:
        result['conversion_note'] = f"Conversion rate not available for {from_currency}"
        logger.warning(f"No conversion rate found for {from_currency}")
        return result
    
    try:
        # Calculate converted amount
        # conversion_rates contains the rate to convert 1 unit TO the base currency
        if to_currency == 'USD':  # Most common base currency
            conversion_rate = conversion_rates[from_currency]
            converted_amount = amount * conversion_rate
        else:
            # Convert through USD if different base currency
            usd_rate = conversion_rates[from_currency]
            to_rate = conversion_rates.get(to_currency, 1.0)
            conversion_rate = usd_rate / to_rate
            converted_amount = amount * conversion_rate
        
        result['converted_amount'] = round(converted_amount, 2)
        result['conversion_rate'] = round(conversion_rate, 6)
        result['conversion_successful'] = True
        result['conversion_note'] = f"Converted via API rates"
        
        # Add validation logging for large differences
        if logger and converted_amount > 0:
            ratio = converted_amount / amount if amount > 0 else 0
            if ratio > 10:  # Converted amount is more than 10x original
                logger.warning(f"Large conversion ratio detected: {amount} {from_currency} -> {converted_amount} {to_currency} (ratio: {ratio:.2f})")
            elif ratio < 0.1:  # Converted amount is less than 1/10 original
                logger.debug(f"Small conversion ratio: {amount} {from_currency} -> {converted_amount} {to_currency} (ratio: {ratio:.6f})")
        
        logger.debug(f"Currency conversion: {amount} {from_currency} = {converted_amount:.2f} {to_currency} (rate: {conversion_rate:.6f})")
        
    except Exception as e:
        result['conversion_note'] = f"Conversion calculation error: {str(e)}"
        logger.error(f"Currency conversion error: {e}")
    
    return result

def get_target_currency_from_config(logger, args=None) -> str:
    """
    Get target currency from command line arguments, environment variables, or default.
    
    Args:
        logger: Logger instance
        args: Command line arguments (optional)
        
    Returns:
        Target currency code (default: USD)
    """
    # Try command line argument first
    if args and hasattr(args, 'target_currency') and args.target_currency:
        target_currency = args.target_currency.upper().strip()
        logger.info(f"Using target currency from command line: {target_currency}")
        return target_currency
    
    # Try environment variable
    target_currency = os.getenv('SF_TARGET_CURRENCY', '').upper().strip()
    
    if target_currency:
        logger.info(f"Using target currency from environment: {target_currency}")
        return target_currency
    
    # Use USD as default
    default_currency = 'USD'
    logger.info(f"Using default target currency: {default_currency}")
    
    return default_currency

def query_opportunity_data(sf, opportunity_id: str, logger, target_currency: str = 'USD') -> Optional[Dict[str, Any]]:
    """
    Query Salesforce for comprehensive opportunity data.
    
    Uses only standard Salesforce fields to ensure compatibility with all orgs.
    
    Args:
        sf: Authenticated Salesforce connection
        opportunity_id: Salesforce opportunity ID
        logger: Logger instance
        
    Returns:
        Dictionary with opportunity data or None if not found
    """
    try:
        # SOQL query with only universally available standard fields
        soql_query = f"""
        SELECT 
            Id,
            Name,
            Account.Id,
            Account.Name,
            CloseDate,
            Amount,
            CurrencyIsoCode,
            StageName,
            Type,
            Probability,
            IsWon,
            IsClosed,
            CreatedDate,
            LastModifiedDate,
            Owner.Name,
            Owner.Id,
            Description
        FROM Opportunity 
        WHERE Id = '{opportunity_id}'
        """
        
        logger.info(f"Querying Salesforce for opportunity: {opportunity_id}")
        logger.debug(f"SOQL Query: {soql_query}")
        
        result = sf.query(soql_query)
        
        if result['totalSize'] == 0:
            logger.warning(f"No opportunity found with ID: {opportunity_id} - creating 'not found' record")
            
            # Create a special document for missing/deleted opportunities
            not_found_data = {
                'opportunity_id': opportunity_id,
                'opportunity_name': 'OPPORTUNITY NOT FOUND',
                'description': 'opportunity deleted or not found',
                'amount': 0.0,
                'currency_iso_code': 'USD',
                'amount_converted': 0.0,
                'converted_currency': target_currency,
                'conversion_rate': 1.0,
                'conversion_successful': True,
                'conversion_note': 'No amount to convert',
                'close_date': None,
                'stage_name': 'NOT_FOUND',
                'type': 'MISSING',
                'probability': 0.0,
                'is_won': False,
                'is_closed': False,
                'account_id': None,
                'account_name': 'UNKNOWN',
                'owner_id': None,
                'owner_name': 'UNKNOWN',
                'created_date': None,
                'last_modified_date': None,
                'extracted_at': datetime.utcnow().isoformat(),
                'source': 'salesforce_opportunity_integration_not_found',
                'error_status': 'OPPORTUNITY_NOT_FOUND',
                'error_message': 'opportunity deleted or not found'
            }
            
            return not_found_data
            
        opportunity = result['records'][0]
        logger.debug(f"Raw Salesforce data: {json.dumps(opportunity, indent=2, default=str)}")
        
        # Get currency conversion rates  
        conversion_rates = get_currency_conversion_rates(target_currency, logger)
        
        # Extract currency information
        original_currency = opportunity.get('CurrencyIsoCode', 'USD')
        original_amount = float(opportunity['Amount']) if opportunity.get('Amount') else 0.0
        
        # Convert currency
        currency_conversion = convert_currency_amount(
            original_amount, 
            original_currency, 
            target_currency, 
            conversion_rates, 
            logger
        )
        
        # Extract and format the data with universally compatible fields
        data = {
            # Core opportunity fields
            'opportunity_id': opportunity['Id'],
            'opportunity_name': opportunity['Name'],
            'description': opportunity.get('Description'),
            
            # Financial data (original and converted)
            'amount': original_amount,
            'currency_iso_code': original_currency,
            'amount_converted': currency_conversion['converted_amount'],
            'converted_currency': currency_conversion['converted_currency'],
            'conversion_rate': currency_conversion['conversion_rate'],
            'conversion_successful': currency_conversion['conversion_successful'],
            'conversion_note': currency_conversion['conversion_note'],
            'close_date': opportunity.get('CloseDate'),
            
            # Stage and status information
            'stage_name': opportunity.get('StageName'),
            'type': opportunity.get('Type'),
            'probability': float(opportunity['Probability']) if opportunity.get('Probability') else 0.0,
            'is_won': bool(opportunity.get('IsWon', False)),
            'is_closed': bool(opportunity.get('IsClosed', False)),
            
            # Account information
            'account_id': opportunity['Account']['Id'] if opportunity.get('Account') else None,
            'account_name': opportunity['Account']['Name'] if opportunity.get('Account') else None,
            
            # Owner information
            'owner_id': opportunity['Owner']['Id'] if opportunity.get('Owner') else None,
            'owner_name': opportunity['Owner']['Name'] if opportunity.get('Owner') else None,
            
            # Audit information
            'created_date': opportunity.get('CreatedDate'),
            'last_modified_date': opportunity.get('LastModifiedDate'),
            
            # Metadata
            'extracted_at': datetime.utcnow().isoformat(),
            'source': 'salesforce_opportunity_integration'
        }
        
        logger.info(f"Successfully extracted opportunity data: {data['opportunity_name']}")
        logger.debug(f"Processed data: {json.dumps(data, indent=2, default=str)}")
        
        return data
        
    except Exception as e:
        error_str = str(e)
        
        # Enhanced error handling for common issues
        if "No such column" in error_str and "__c" in error_str:
            logger.error(f"Custom field error: {error_str}")
            logger.error("A custom field referenced in the query doesn't exist in your Salesforce org.")
            error_type = "CUSTOM_FIELD_ERROR"
            error_message = f"Custom field error: {error_str}"
        elif "INVALID_FIELD" in error_str:
            logger.error(f"Invalid field error: {error_str}")
            logger.error("One or more fields in the query don't exist in your Salesforce org.")
            error_type = "INVALID_FIELD_ERROR"
            error_message = f"Invalid field error: {error_str}"
        elif "MALFORMED_QUERY" in error_str:
            logger.error(f"Malformed query error: {error_str}")
            logger.error("There's a syntax error in the SOQL query.")
            error_type = "MALFORMED_QUERY_ERROR"
            error_message = f"Malformed query error: {error_str}"
        elif "INSUFFICIENT_ACCESS" in error_str:
            logger.error(f"Access error: {error_str}")
            error_type = "ACCESS_ERROR"
            error_message = f"Insufficient access to query opportunity: {error_str}"
        else:
            logger.error(f"Error querying Salesforce: {error_str}")
            error_type = "QUERY_ERROR"
            error_message = f"Error querying Salesforce: {error_str}"
        
        # Create an error document for Elasticsearch
        logger.info(f"Creating error document for opportunity {opportunity_id}")
        error_data = {
            'opportunity_id': opportunity_id,
            'opportunity_name': f'ERROR: {error_type}',
            'description': error_message,
            'amount': 0.0,
            'currency_iso_code': 'USD',
            'amount_converted': 0.0,
            'converted_currency': target_currency,
            'conversion_rate': 1.0,
            'conversion_successful': True,
            'conversion_note': 'No amount to convert (error)',
            'close_date': None,
            'stage_name': 'ERROR',
            'type': 'ERROR',
            'probability': 0.0,
            'is_won': False,
            'is_closed': False,
            'account_id': None,
            'account_name': 'ERROR',
            'owner_id': None,
            'owner_name': 'ERROR',
            'created_date': None,
            'last_modified_date': None,
            'extracted_at': datetime.utcnow().isoformat(),
            'source': 'salesforce_opportunity_integration_error',
            'error_status': error_type,
            'error_message': error_message
        }
        
        return error_data

def get_elasticsearch_config(logger) -> Optional[Dict[str, Any]]:
    """
    Get Elasticsearch configuration from environment variables or user input.
    
    Args:
        logger: Logger instance
        
    Returns:
        Dictionary with ES configuration or None if not available
    """
    config = {}
    
    # Try to get configuration from environment variables first
    config['cluster_url'] = os.getenv('ES_CLUSTER_URL')
    config['username'] = os.getenv('ES_USERNAME')
    config['password'] = os.getenv('ES_PASSWORD')
    config['api_key'] = os.getenv('ES_API_KEY')
    config['index'] = os.getenv('ES_INDEX', 'salesforce-opportunities')
    
    # Check if we have either username/password or API key
    has_auth = (config['username'] and config['password']) or config['api_key']
    
    if config['cluster_url'] and has_auth:
        logger.info("Using Elasticsearch configuration from environment variables")
        config['auth_type'] = 'api_key' if config['api_key'] else 'basic'
        return config
    
    # If no environment variables, prompt user
    print("\n🔧 Elasticsearch Configuration")
    print("=" * 40)
    print("Environment variables not set. Please provide Elasticsearch details:")
    
    try:
        config['cluster_url'] = input("Elasticsearch URL: ").strip()
        if not config['cluster_url']:
            logger.warning("No Elasticsearch URL provided")
            return None
        
        auth_choice = input("Use API key auth? (y/n, default: n): ").strip().lower()
        
        if auth_choice in ['y', 'yes']:
            config['api_key'] = input("API Key: ").strip()
            config['auth_type'] = 'api_key'
        else:
            config['username'] = input("Username: ").strip()
            config['password'] = input("Password: ").strip()
            config['auth_type'] = 'basic'
        
        config['index'] = input(f"Index name (default: salesforce-opportunities): ").strip()
        if not config['index']:
            config['index'] = 'salesforce-opportunities'
        
        return config
        
    except (KeyboardInterrupt, EOFError):
        print("\n⚠️  Configuration cancelled")
        return None

def validate_elasticsearch_config(config: Dict[str, Any], logger) -> bool:
    """
    Validate Elasticsearch configuration.
    
    Args:
        config: ES configuration dictionary
        logger: Logger instance
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['cluster_url', 'index', 'auth_type']
    
    for field in required_fields:
        if not config.get(field):
            logger.error(f"Missing required Elasticsearch config: {field}")
            return False
    
    if config['auth_type'] == 'basic':
        if not config.get('username') or not config.get('password'):
            logger.error("Username and password required for basic auth")
            return False
    elif config['auth_type'] == 'api_key':
        if not config.get('api_key'):
            logger.error("API key required for API key auth")
            return False
    
    # Validate URL format
    if not config['cluster_url'].startswith(('http://', 'https://')):
        logger.error("Elasticsearch URL must start with http:// or https://")
        return False
    
    return True

def connect_elasticsearch(config: Dict[str, Any], logger) -> Optional[Elasticsearch]:
    """
    Connect to Elasticsearch with the provided configuration.
    
    Args:
        config: ES configuration dictionary
        logger: Logger instance
        
    Returns:
        Elasticsearch client or None if connection failed
    """
    if not ELASTICSEARCH_AVAILABLE:
        logger.error("Elasticsearch library not available. Install with: pip install elasticsearch")
        return None
    
    try:
        # Build connection parameters
        connection_params = {
            'verify_certs': False,
            'request_timeout': 30,
            'retry_on_timeout': True,
            'max_retries': 3
        }
        
        # Add authentication
        if config['auth_type'] == 'api_key':
            connection_params['api_key'] = config['api_key']
        else:
            connection_params['basic_auth'] = (config['username'], config['password'])
        
        # Create connection
        es = Elasticsearch(
            [config['cluster_url']],
            **connection_params
        )
        
        # Test connection
        info = es.info()
        logger.info(f"Connected to Elasticsearch cluster: {info.body['name']} (version: {info.body['version']['number']})")
        return es
        
    except ConnectionError as e:
        logger.error(f"Could not connect to Elasticsearch: {e}")
        logger.error("Please check the cluster URL and network connectivity")
        return None
    except AuthenticationException as e:
        logger.error(f"Elasticsearch authentication failed: {e}")
        logger.error("Please check your credentials")
        return None
    except Exception as e:
        logger.error(f"Unexpected Elasticsearch connection error: {e}")
        return None

def create_elasticsearch_index(es: Elasticsearch, index_name: str, logger) -> bool:
    """
    Create Elasticsearch index with optimized mapping for opportunity data.
    
    Args:
        es: Elasticsearch client
        index_name: Name of the index to create
        logger: Logger instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if index already exists
        if es.indices.exists(index=index_name):
            logger.info(f"Index '{index_name}' already exists")
            return True
        
        # Define mapping optimized for universally available opportunity fields
        mapping = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1,
                "analysis": {
                    "analyzer": {
                        "standard_lowercase": {
                            "type": "standard",
                            "lowercase": True
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    # Core opportunity fields
                    "opportunity_id": {"type": "keyword"},
                    "opportunity_name": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                        "analyzer": "standard_lowercase"
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "standard_lowercase"
                    },
                    
                    # Financial fields (original and converted)
                    "amount": {"type": "double"},
                    "currency_iso_code": {"type": "keyword"},
                    "amount_converted": {"type": "double"},
                    "converted_currency": {"type": "keyword"},
                    "conversion_rate": {"type": "double"},
                    "conversion_successful": {"type": "boolean"},
                    "conversion_note": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}}
                    },
                    "close_date": {"type": "date"},
                    
                    # Stage and status fields
                    "stage_name": {"type": "keyword"},
                    "type": {"type": "keyword"},
                    "probability": {"type": "double"},
                    "is_won": {"type": "boolean"},
                    "is_closed": {"type": "boolean"},
                    
                    # Account fields
                    "account_id": {"type": "keyword"},
                    "account_name": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                        "analyzer": "standard_lowercase"
                    },
                    
                    # Owner fields
                    "owner_id": {"type": "keyword"},
                    "owner_name": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}}
                    },
                    
                    # Audit fields
                    "created_date": {"type": "date"},
                    "last_modified_date": {"type": "date"},
                    
                    # Metadata fields
                    "extracted_at": {"type": "date"},
                    "source": {"type": "keyword"},
                    
                    # Error handling fields
                    "error_status": {"type": "keyword"},
                    "error_message": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}}
                    }
                }
            }
        }
        
        # Create the index
        response = es.indices.create(index=index_name, body=mapping)
        logger.info(f"Created index '{index_name}' with optimized mapping")
        logger.debug(f"Index creation response: {response}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating index '{index_name}': {e}")
        return False

def index_opportunity_data(es: Elasticsearch, data: Dict[str, Any], index_name: str, logger) -> bool:
    """
    Index opportunity data into Elasticsearch.
    
    Args:
        es: Elasticsearch client
        data: Opportunity data to index
        index_name: Target index name
        logger: Logger instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Use opportunity ID as document ID to prevent duplicates
        doc_id = data['opportunity_id']
        
        # Index the document
        response = es.index(
            index=index_name,
            id=doc_id,
            body=data
        )
        
        result = response['result']
        logger.info(f"Document indexed successfully: {doc_id} (result: {result})")
        
        if result == 'created':
            logger.info("New document created in Elasticsearch")
        elif result == 'updated':
            logger.info("Existing document updated in Elasticsearch")
        
        return True
        
    except RequestError as e:
        logger.error(f"Elasticsearch indexing error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during indexing: {e}")
        return False

def save_json_output(data: Dict[str, Any], output_file: Optional[str], logger) -> bool:
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        output_file: Output filename (optional)
        logger: Logger instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Generate filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            opp_id = data.get('opportunity_id', 'unknown')
            output_file = f"opportunity_{opp_id}_{timestamp}.json"
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Data saved to JSON file: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving JSON file: {e}")
        return False

def display_opportunity_summary(data: Dict[str, Any], logger):
    """
    Display a summary of the extracted opportunity data.
    
    Args:
        data: Opportunity data (or error data)
        logger: Logger instance
    """
    print(f"\n📊 OPPORTUNITY SUMMARY")
    print("=" * 50)
    
    # Check if this is an error document
    is_error_document = data.get('error_status') is not None
    
    if is_error_document:
        # Display error information
        print(f"⚠️  Status: {data.get('error_status', 'UNKNOWN_ERROR')}")
        print(f"🎯 Opportunity ID: {data.get('opportunity_id', 'Unknown')}")
        print(f"❌ Error: {data.get('error_message', 'Unknown error occurred')}")
        print(f"🕐 Processed: {data.get('extracted_at', 'Unknown')[:19]}")
        
        # Add specific guidance based on error type
        error_status = data.get('error_status', '')
        if error_status == 'OPPORTUNITY_NOT_FOUND':
            print(f"💡 Note: This opportunity may have been deleted or you don't have access to it")
        elif 'FIELD_ERROR' in error_status:
            print(f"💡 Note: This is a field configuration issue in your Salesforce org")
        elif 'ACCESS_ERROR' in error_status:
            print(f"💡 Note: Check your Salesforce permissions for this opportunity")
    else:
        # Display normal opportunity information
        print(f"🎯 Opportunity: {data.get('opportunity_name', 'Unknown')}")
        print(f"🏢 Account: {data.get('account_name', 'Unknown')}")
        
        # Currency and amount information
        original_amount = data.get('amount', 0)
        original_currency = data.get('currency_iso_code', 'USD')
        converted_amount = data.get('amount_converted', 0)
        converted_currency = data.get('converted_currency', 'USD')
        conversion_successful = data.get('conversion_successful', False)
        
        if conversion_successful and original_currency != converted_currency:
            print(f"💰 Amount: {original_amount:,.2f} {original_currency} = {converted_amount:,.2f} {converted_currency}")
            conversion_rate = data.get('conversion_rate', 1.0)
            print(f"🔄 Conversion: 1 {original_currency} = {conversion_rate:.6f} {converted_currency}")
        else:
            print(f"💰 Amount: {original_amount:,.2f} {original_currency}")
            if not conversion_successful:
                print(f"⚠️  Currency: {data.get('conversion_note', 'Conversion not available')}")
        
        print(f"📈 Stage: {data.get('stage_name', 'Unknown')}")
        print(f"📅 Close Date: {data.get('close_date', 'Not set')}")
        print(f"🎲 Probability: {data.get('probability', 0)}%")
        
        # Status information
        status = "WON" if data.get('is_won') else "LOST" if data.get('is_closed') else "OPEN"
        print(f"📋 Status: {status}")
        
        # Owner information
        if data.get('owner_name') and data.get('owner_name') != 'ERROR':
            print(f"👤 Owner: {data['owner_name']}")
        
        # Timeline
        if data.get('created_date'):
            print(f"📅 Created: {data['created_date'][:10]}")
        
        print(f"🕐 Extracted: {data.get('extracted_at', 'Unknown')[:19]}")

def read_urls_from_file(file_path: str, logger) -> List[str]:
    """
    Read opportunity URLs from a text file.
    
    Args:
        file_path: Path to text file containing URLs
        logger: Logger instance
        
    Returns:
        List of valid URLs
    """
    urls = []
    
    try:
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Validate URL format
                if validate_opportunity_url(line):
                    urls.append(line)
                    logger.debug(f"Added valid URL from line {line_num}: {line}")
                else:
                    logger.warning(f"Invalid URL on line {line_num}: {line}")
        
        logger.info(f"Read {len(urls)} valid URLs from {file_path}")
        return urls
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return []
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return []

def process_single_opportunity(sf, url: str, es, es_config: Optional[Dict[str, Any]], 
                             args, logger) -> Dict[str, Any]:
    """
    Process a single opportunity URL.
    
    Args:
        sf: Salesforce connection
        url: Opportunity URL
        es: Elasticsearch client (optional)
        es_config: Elasticsearch configuration (optional)
        args: Command line arguments
        logger: Logger instance
        
    Returns:
        Dictionary with processing results
    """
    result = {
        'url': url,
        'success': False,
        'opportunity_id': None,
        'opportunity_name': None,
        'error': None,
        'data': None
    }
    
    try:
        # Extract opportunity ID
        opportunity_id = extract_opportunity_id(url)
        if not opportunity_id:
            result['error'] = "Could not extract opportunity ID from URL"
            return result
        
        result['opportunity_id'] = opportunity_id
        logger.debug(f"Processing opportunity: {opportunity_id}")
        
        # Get target currency for conversion
        target_currency = get_target_currency_from_config(logger, args)
        
        # Query opportunity data (always returns data - either valid or error)
        data = query_opportunity_data(sf, opportunity_id, logger, target_currency)
        if not data:
            # This should never happen now, but keep as fallback
            result['error'] = "Failed to retrieve opportunity data - unexpected None response"
            return result
        
        result['data'] = data
        result['opportunity_name'] = data.get('opportunity_name', 'Unknown')
        
        # Check if this is an error document
        is_error_document = data.get('error_status') is not None
        if is_error_document:
            result['error'] = data.get('error_message', 'Unknown error')
            logger.warning(f"Error document created for {opportunity_id}: {result['error']}")
        
        # Index to Elasticsearch if configured (including error documents)
        if not args.json_only and es and es_config:
            if not index_opportunity_data(es, data, es_config['index'], logger):
                additional_error = "Failed to index to Elasticsearch"
                if is_error_document:
                    result['error'] = f"{result['error']} + {additional_error}"
                else:
                    result['error'] = additional_error
                # Don't return here - still successful for JSON
        
        result['success'] = True
        
        # Log different messages for error vs. normal documents
        if is_error_document:
            logger.info(f"Processed error document for {opportunity_id}: {data.get('error_status', 'UNKNOWN_ERROR')}")
        else:
            logger.info(f"Successfully processed: {result['opportunity_name']}")

        
    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Error processing {url}: {e}")
    
    return result

def save_batch_results(results: List[Dict[str, Any]], args, logger) -> bool:
    """
    Save batch processing results to JSON files.
    
    Args:
        results: List of processing results
        args: Command line arguments
        logger: Logger instance
        
    Returns:
        True if successful
    """
    import os
    
    try:
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)
        
        successful_results = [r for r in results if r['success']]
        
        if args.combined_json:
            # Save all successful results to single file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = args.output_file or f"batch_opportunities_{timestamp}.json"
            filepath = os.path.join(args.output_dir, filename)
            
            batch_data = {
                'metadata': {
                    'total_processed': len(results),
                    'successful': len(successful_results),
                    'failed': len(results) - len(successful_results),
                    'generated_at': datetime.utcnow().isoformat(),
                    'source': 'sf_to_elasticsearch_batch'
                },
                'opportunities': [r['data'] for r in successful_results]
            }
            
            with open(filepath, 'w') as f:
                json.dump(batch_data, f, indent=2, default=str)
            
            logger.info(f"Saved combined results to: {filepath}")
            
        else:
            # Save individual files
            for result in successful_results:
                if result['data']:
                    opp_id = result['opportunity_id']
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"opportunity_{opp_id}_{timestamp}.json"
                    filepath = os.path.join(args.output_dir, filename)
                    
                    with open(filepath, 'w') as f:
                        json.dump(result['data'], f, indent=2, default=str)
                    
                    logger.debug(f"Saved individual result to: {filepath}")
            
            logger.info(f"Saved {len(successful_results)} individual files to: {args.output_dir}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error saving batch results: {e}")
        return False

def display_batch_summary(results: List[Dict[str, Any]], logger):
    """
    Display summary of batch processing results.
    
    Args:
        results: List of processing results
        logger: Logger instance
    """
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    # Categorize successful results into normal vs error documents
    normal_opportunities = []
    error_documents = []
    
    for result in successful:
        if result['data'] and result['data'].get('error_status'):
            error_documents.append(result)
        else:
            normal_opportunities.append(result)
    
    print(f"\n📊 BATCH PROCESSING SUMMARY")
    print("=" * 50)
    print(f"📈 Total URLs: {len(results)}")
    print(f"✅ Successfully Processed: {len(successful)}")
    print(f"   📊 Normal Opportunities: {len(normal_opportunities)}")
    print(f"   ⚠️  Error Documents: {len(error_documents)}")
    print(f"❌ Failed: {len(failed)}")
    
    if successful:
        success_rate = (len(successful) / len(results)) * 100
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        # Show normal opportunities
        if normal_opportunities:
            print(f"\n✅ Normal Opportunities:")
            for i, result in enumerate(normal_opportunities[:5], 1):
                opp_name = result['opportunity_name'][:50]
                data = result['data'] if result['data'] else {}
                
                # Get currency information
                converted_amount = data.get('amount_converted', 0)
                converted_currency = data.get('converted_currency', 'USD')
                original_amount = data.get('amount', 0)
                original_currency = data.get('currency_iso_code', 'USD')
                conversion_successful = data.get('conversion_successful', False)
                
                stage = data.get('stage_name', 'Unknown')
                
                # Display amount with currency
                if conversion_successful and original_currency != converted_currency:
                    amount_display = f"{converted_amount:,.0f} {converted_currency} ({original_amount:,.0f} {original_currency})"
                else:
                    amount_display = f"{original_amount:,.0f} {original_currency}"
                
                print(f"   {i}. {opp_name} - {amount_display} - {stage}")
            
            if len(normal_opportunities) > 5:
                print(f"   ... and {len(normal_opportunities) - 5} more")
        
        # Show error documents (deleted/missing opportunities)
        if error_documents:
            print(f"\n⚠️  Error Documents (Deleted/Missing Opportunities):")
            for i, result in enumerate(error_documents[:5], 1):
                opp_id = result['opportunity_id'] or 'Unknown'
                error_status = result['data'].get('error_status', 'UNKNOWN') if result['data'] else 'UNKNOWN'
                error_msg = result['data'].get('error_message', 'Unknown error')[:60] if result['data'] else 'Unknown error'
                print(f"   {i}. {opp_id}: {error_status} - {error_msg}")
            
            if len(error_documents) > 5:
                print(f"   ... and {len(error_documents) - 5} more error documents")
    
    if failed:
        print(f"\n❌ Processing Failures:")
        for i, result in enumerate(failed[:5], 1):
            error = result['error'][:60] + "..." if len(result['error']) > 60 else result['error']
            print(f"   {i}. {result['opportunity_id'] or 'Unknown'}: {error}")
        
        if len(failed) > 5:
            print(f"   ... and {len(failed) - 5} more failures")
    
    # Summary insights
    if error_documents:
        print(f"\n💡 Note: Error documents are indexed in Elasticsearch for audit purposes.")
        print(f"   You can query them using: error_status:OPPORTUNITY_NOT_FOUND")

def main():
    """Main function."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Salesforce to Elasticsearch Integration')
    
    # Input options - either single URL or file
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('opportunity_url', nargs='?', help='Single Salesforce opportunity URL')
    input_group.add_argument('--file', '-f', dest='urls_file', help='Text file containing opportunity URLs (one per line)')
    
    # Output options
    parser.add_argument('--json-only', action='store_true', help='Output JSON only (skip Elasticsearch)')
    parser.add_argument('--output-file', help='JSON output filename (for single URL) or base filename (for batch)')
    parser.add_argument('--output-dir', default='opportunity_exports', help='Output directory for batch JSON files')
    parser.add_argument('--combined-json', action='store_true', help='Save all opportunities to single JSON file (batch mode)')
    
    # Processing options
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--no-summary', action='store_true', help='Skip opportunity summary display')
    parser.add_argument('--continue-on-error', action='store_true', help='Continue processing if individual URLs fail')
    parser.add_argument('--max-workers', type=int, default=1, help='Maximum concurrent workers (1 = sequential)')
    parser.add_argument('--target-currency', default='USD', help='Target currency for conversion (default: USD)')
    
    # Validation
    parser.add_argument('--validate-only', action='store_true', help='Only validate URLs without processing')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    logger.info("Starting Salesforce to Elasticsearch integration")
    
    # Determine processing mode
    if args.opportunity_url:
        urls = [args.opportunity_url]
        batch_mode = False
        logger.info(f"Processing single URL: {args.opportunity_url}")
    elif args.urls_file:
        urls = read_urls_from_file(args.urls_file, logger)
        batch_mode = True
        logger.info(f"Processing {len(urls)} URLs from file: {args.urls_file}")
        
        if not urls:
            logger.error("No valid URLs found in file")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)
    
    # Validation-only mode
    if args.validate_only:
        print(f"🔍 VALIDATING {len(urls)} URLs")
        print("=" * 40)
        
        valid_count = 0
        for i, url in enumerate(urls, 1):
            opportunity_id = extract_opportunity_id(url)
            if opportunity_id:
                print(f"✅ {i:3d}. {opportunity_id} - {url[:60]}...")
                valid_count += 1
            else:
                print(f"❌ {i:3d}. INVALID - {url[:60]}...")
        
        print(f"\n📊 Validation Summary:")
        print(f"   Valid URLs: {valid_count}/{len(urls)}")
        print(f"   Invalid URLs: {len(urls) - valid_count}/{len(urls)}")
        
        if valid_count == len(urls):
            print("✅ All URLs are valid!")
        else:
            print("⚠️  Some URLs are invalid")
        
        return
    
    # Validate all URLs before processing
    invalid_urls = []
    for url in urls:
        if not validate_opportunity_url(url):
            invalid_urls.append(url)
            logger.warning(f"Invalid URL: {url}")
    
    if invalid_urls and not args.continue_on_error:
        logger.error(f"Found {len(invalid_urls)} invalid URLs")
        print("\nInvalid URLs found:")
        for url in invalid_urls[:5]:
            print(f"  ❌ {url}")
        if len(invalid_urls) > 5:
            print(f"  ... and {len(invalid_urls) - 5} more")
        print("\nUse --continue-on-error to skip invalid URLs")
        sys.exit(1)
    
    # Remove invalid URLs if continuing on error
    if invalid_urls and args.continue_on_error:
        valid_urls = [url for url in urls if url not in invalid_urls]
        logger.info(f"Continuing with {len(valid_urls)} valid URLs (skipped {len(invalid_urls)} invalid)")
        urls = valid_urls
    
    
    # Connect to Salesforce
    print("🔗 Connecting to Salesforce...")
    try:
        sf = get_salesforce_connection()
        logger.info("Connected to Salesforce successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Salesforce: {e}")
        print("❌ Salesforce connection failed")
        print("Please ensure you're authenticated with: sf org login web")
        sys.exit(1)
    
    # Setup Elasticsearch if not JSON-only mode
    es = None
    es_config = None
    
    if not args.json_only:
        if not ELASTICSEARCH_AVAILABLE:
            logger.warning("Elasticsearch library not available - switching to JSON-only mode")
            print("⚠️  Elasticsearch not available, switching to JSON-only mode...")
            args.json_only = True
        else:
            print(f"\n🔧 Configuring Elasticsearch connection...")
            es_config = get_elasticsearch_config(logger)
            
            if not es_config:
                logger.warning("No Elasticsearch configuration provided - switching to JSON-only mode")
                print("⚠️  No Elasticsearch config, switching to JSON-only mode...")
                args.json_only = True
            else:
                # Validate configuration
                if not validate_elasticsearch_config(es_config, logger):
                    logger.error("Invalid Elasticsearch configuration")
                    print("❌ Invalid Elasticsearch configuration, switching to JSON-only mode...")
                    args.json_only = True
                else:
                    # Connect to Elasticsearch
                    print(f"🔍 Connecting to Elasticsearch...")
                    es = connect_elasticsearch(es_config, logger)
                    
                    if not es:
                        logger.error("Failed to connect to Elasticsearch")
                        print("❌ Elasticsearch connection failed, switching to JSON-only mode...")
                        args.json_only = True
                    else:
                        print("✅ Connected to Elasticsearch")
                        
                        # Create index if needed
                        print(f"📋 Setting up index: {es_config['index']}")
                        if not create_elasticsearch_index(es, es_config['index'], logger):
                            logger.error("Failed to create Elasticsearch index")
                            print("❌ Index creation failed, switching to JSON-only mode...")
                            args.json_only = True
    
    if args.json_only:
        print("📄 Operating in JSON-only mode")
    
    # Process opportunities
    if batch_mode:
        print(f"\n📊 Processing {len(urls)} opportunities...")
    else:
        print(f"\n📊 Processing opportunity...")
    
    results = []
    
    for i, url in enumerate(urls, 1):
        if batch_mode:
            print(f"🔄 Processing {i}/{len(urls)}: {extract_opportunity_id(url) or 'Unknown'}")
        
        result = process_single_opportunity(sf, url, es, es_config, args, logger)
        results.append(result)
        
        # Display individual summary for single URL mode
        if not batch_mode and not args.no_summary and result['success'] and result['data']:
            display_opportunity_summary(result['data'], logger)
        
        # Stop on error if not continuing
        if not result['success'] and not args.continue_on_error:
            logger.error(f"Processing failed for {url}: {result['error']}")
            print(f"❌ Processing failed: {result['error']}")
            sys.exit(1)
    
    # Display batch summary
    if batch_mode:
        display_batch_summary(results, logger)
    
    # Save results to JSON
    if args.json_only or args.output_file or batch_mode:
        if batch_mode:
            print(f"\n💾 Saving batch results...")
            if save_batch_results(results, args, logger):
                print(f"✅ Results saved to: {args.output_dir}")
            else:
                print("❌ Failed to save batch results")
        else:
            # Single URL mode
            successful_result = next((r for r in results if r['success']), None)
            if successful_result and successful_result['data']:
                print(f"\n💾 Saving data to JSON file...")
                if save_json_output(successful_result['data'], args.output_file, logger):
                    print("✅ JSON file saved successfully")
                else:
                    print("❌ Failed to save JSON file")
    
    # Final summary
    successful_count = sum(1 for r in results if r['success'])
    
    if batch_mode:
        print(f"\n🎉 Batch processing completed!")
        print(f"   ✅ Successful: {successful_count}/{len(results)}")
        
        if not args.json_only and es:
            print(f"   📤 Indexed to Elasticsearch: {es_config['index']}")
        
        if args.json_only:
            print(f"   📄 JSON files saved to: {args.output_dir}")
    else:
        if successful_count > 0:
            print(f"\n🎉 Integration completed successfully!")
            if not args.json_only and es:
                print(f"   📤 Indexed to Elasticsearch: {es_config['index']}")
        else:
            print(f"\n❌ Integration failed")
            sys.exit(1)
    
    logger.info("Salesforce to Elasticsearch integration completed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
