#!/usr/bin/env python3
"""
Configuration module for Salesforce to Elasticsearch Integration Tool

This module handles all configuration settings for connecting to Elasticsearch
and Salesforce, including interactive prompts and environment variable support.
"""

import getpass
import os
import sys
from typing import Dict, Any, Tuple

# ============================================================================
# DEFAULT CONFIGURATION VALUES
# ============================================================================

# Elasticsearch Configuration
ES_CLUSTER_URL = None  # Set dynamically via prompts or environment variables
ES_USERNAME = None     # Set dynamically via prompts or environment variables 
ES_PASSWORD = None     # Set dynamically via prompts or environment variables
ES_API_KEY = None      # Alternative to username/password authentication
ES_INDEX = "specialist-engagements"  # Default index name, can be overridden
ES_VERIFY_CERTS = False  # Always disable SSL verification for flexibility

# Salesforce Configuration (managed by sf_auth.py)
SF_INSTANCE_URL = "https://elastic.my.salesforce.com"
SF_ORG_ALIAS = "elastic"

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "sf_to_es.log"

# Elasticsearch Index Mapping Template
INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "opportunity_id": {"type": "keyword"},
            "opportunity_name": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}}
            },
            "account_name": {
                "type": "text", 
                "fields": {"keyword": {"type": "keyword"}}
            },
            "close_date": {"type": "date"},
            "amount": {"type": "double"},
            "tcv_amount": {"type": "double"},
            "extracted_at": {"type": "date"},
            "source": {"type": "keyword"}
        }
    }
}

# ============================================================================
# INTERACTIVE CONFIGURATION FUNCTIONS
# ============================================================================

def get_elasticsearch_config(silent=False) -> Dict[str, Any]:
    """
    Interactively collect Elasticsearch configuration from user.
    
    Args:
        silent: If True, suppress print statements (useful for testing)
    
    Returns:
        Dictionary with Elasticsearch connection parameters
    """
    if not silent:
        print("\n🔧 Elasticsearch Configuration")
        print("=" * 40)
    
    # Get cluster URL
    default_url = "https://your-cluster.es.region.aws.elastic-cloud.com"
    if not silent:
        cluster_url = input(f"Elasticsearch cluster URL [{default_url}]: ").strip()
    else:
        cluster_url = os.environ.get('ES_CLUSTER_URL', default_url)
    
    if not cluster_url:
        cluster_url = default_url
    
    # Get index name
    if not silent:
        index_name = input(f"Index name [{ES_INDEX}]: ").strip()
    else:
        index_name = os.environ.get('ES_INDEX', ES_INDEX)
    
    if not index_name:
        index_name = ES_INDEX
    
    # Choose authentication method
    if not silent:
        print("\nAuthentication method:")
        print("1. Username and password")
        print("2. API key")
        auth_choice = input("Choose (1/2): ").strip()
    else:
        # For silent mode, check if API key is set, otherwise use username/password
        auth_choice = "2" if os.environ.get('ES_API_KEY') else "1"
    
    config = {
        'cluster_url': cluster_url,
        'index': index_name,
        'verify_certs': ES_VERIFY_CERTS
    }
    
    if auth_choice == '2':
        # API key authentication
        if not silent:
            api_key = getpass.getpass("Enter API key: ").strip()
        else:
            api_key = os.environ.get('ES_API_KEY', '')
        
        config.update({
            'auth_type': 'api_key',
            'api_key': api_key
        })
    else:
        # Username/password authentication (default)
        if not silent:
            username = input("Username: ").strip()
            password = getpass.getpass("Password: ").strip()
        else:
            username = os.environ.get('ES_USERNAME', '')
            password = os.environ.get('ES_PASSWORD', '')
        
        config.update({
            'auth_type': 'basic',
            'username': username,
            'password': password
        })
    
    return config

def get_elasticsearch_config_from_env() -> Dict[str, Any]:
    """
    Get Elasticsearch configuration from environment variables.
    Useful for non-interactive scripts and automation.
    
    Returns:
        Dictionary with Elasticsearch connection parameters
    
    Environment Variables:
        ES_CLUSTER_URL: Elasticsearch cluster URL
        ES_INDEX: Index name (optional, defaults to 'specialist-engagements')
        ES_API_KEY: API key for authentication (alternative to username/password)
        ES_USERNAME: Username for basic authentication  
        ES_PASSWORD: Password for basic authentication
    """
    config = {
        'cluster_url': os.environ.get('ES_CLUSTER_URL'),
        'index': os.environ.get('ES_INDEX', ES_INDEX),
        'verify_certs': ES_VERIFY_CERTS
    }
    
    # Check for API key first (preferred method)
    api_key = os.environ.get('ES_API_KEY')
    if api_key:
        config.update({
            'auth_type': 'api_key',
            'api_key': api_key
        })
    else:
        # Fall back to username/password
        config.update({
            'auth_type': 'basic',
            'username': os.environ.get('ES_USERNAME'),
            'password': os.environ.get('ES_PASSWORD')
        })
    
    return config

# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_es_config(config: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate that required Elasticsearch configuration values are present.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    # Check cluster URL
    if not config.get('cluster_url'):
        return False, "Cluster URL is required"
    
    # Validate URL format
    cluster_url = config['cluster_url']
    if not cluster_url.startswith(('http://', 'https://')):
        return False, "Cluster URL must start with http:// or https://"
    
    # Check authentication credentials
    auth_type = config.get('auth_type', 'basic')
    
    if auth_type == 'api_key':
        if not config.get('api_key'):
            return False, "API key is required for API key authentication"
        if len(config['api_key']) < 10:  # Basic sanity check
            return False, "API key appears to be too short"
    else:
        if not config.get('username'):
            return False, "Username is required for basic authentication"
        if not config.get('password'):
            return False, "Password is required for basic authentication"
    
    # Check index name
    if not config.get('index'):
        return False, "Index name is required"
    
    # Validate index name (Elasticsearch naming rules)
    index_name = config['index']
    if not index_name.islower():
        return False, "Index name must be lowercase"
    
    if any(char in index_name for char in [' ', '"', '*', '\\', '<', '|', ',', '>', '/', '?']):
        return False, "Index name contains invalid characters"
    
    return True, "Configuration is valid"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def print_config_summary(config: Dict[str, Any]) -> None:
    """
    Print a summary of the current configuration (without sensitive data).
    
    Args:
        config: Configuration dictionary to summarize
    """
    print("\n📋 Configuration Summary:")
    print(f"   Cluster URL: {config.get('cluster_url', 'Not set')}")
    print(f"   Index: {config.get('index', 'Not set')}")
    print(f"   SSL Verification: {'Enabled' if config.get('verify_certs') else 'Disabled'}")
    
    auth_type = config.get('auth_type', 'basic')
    if auth_type == 'api_key':
        api_key = config.get('api_key', '')
        masked_key = api_key[:8] + '...' if len(api_key) > 8 else '[HIDDEN]'
        print(f"   Authentication: API Key ({masked_key})")
    else:
        username = config.get('username', 'Not set')
        print(f"   Authentication: Username/Password ({username})")

def get_config_interactive_or_env() -> Dict[str, Any]:
    """
    Get configuration from environment variables first, fall back to interactive.
    This is useful for scripts that can run in both automated and manual modes.
    
    Returns:
        Valid Elasticsearch configuration dictionary
    """
    # Try environment variables first
    config = get_elasticsearch_config_from_env()
    is_valid, error_msg = validate_es_config(config)
    
    if is_valid:
        print("✅ Using configuration from environment variables")
        return config
    
    # Fall back to interactive configuration
    print("⚠️  Environment configuration incomplete, switching to interactive mode")
    print(f"   Reason: {error_msg}")
    
    config = get_elasticsearch_config()
    is_valid, error_msg = validate_es_config(config)
    
    if not is_valid:
        raise ValueError(f"Invalid configuration: {error_msg}")
    
    return config

# ============================================================================
# SALESFORCE CONFIGURATION (for reference)
# ============================================================================

def get_salesforce_config() -> Dict[str, str]:
    """
    Get Salesforce configuration (managed by sf_auth.py).
    This function is provided for completeness but authentication
    is handled by the sf_auth module.
    
    Returns:
        Dictionary with Salesforce configuration
    """
    return {
        'instance_url': SF_INSTANCE_URL,
        'org_alias': SF_ORG_ALIAS
    }

# ============================================================================
# MAIN EXECUTION (for testing)
# ============================================================================

if __name__ == "__main__":
    """Test the configuration functions."""
    print("🧪 Testing Elasticsearch Configuration Functions")
    print("=" * 50)
    
    # Test environment variable config
    print("\n1. Testing environment variable configuration...")
    env_config = get_elasticsearch_config_from_env()
    is_valid, msg = validate_es_config(env_config)
    print(f"   Valid: {is_valid}, Message: {msg}")
    
    # Test validation with sample configs
    print("\n2. Testing validation with sample configurations...")
    
    # Valid config
    valid_config = {
        'cluster_url': 'https://test-cluster.es.us-east-1.aws.elastic-cloud.com',
        'index': 'test-index',
        'auth_type': 'basic',
        'username': 'test_user',
        'password': 'test_pass',
        'verify_certs': False
    }
    
    is_valid, msg = validate_es_config(valid_config)
    print(f"   Valid config test: {is_valid}, Message: {msg}")
    
    # Invalid config (missing password)
    invalid_config = {
        'cluster_url': 'https://test-cluster.es.us-east-1.aws.elastic-cloud.com',
        'index': 'test-index',
        'auth_type': 'basic',
        'username': 'test_user',
        'verify_certs': False
    }
    
    is_valid, msg = validate_es_config(invalid_config)
    print(f"   Invalid config test: {is_valid}, Message: {msg}")
    
    print("\n✅ Configuration module test complete!")
