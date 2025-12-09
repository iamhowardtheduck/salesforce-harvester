#!/usr/bin/env python3
"""
Elasticsearch Connection Diagnostics

This script helps troubleshoot why data isn't being loaded into Elasticsearch
even when environment variables are set correctly.

Usage:
    python3 es_diagnostics.py
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment_variables() -> Dict[str, Any]:
    """Check what ES environment variables are set."""
    
    print("🔍 CHECKING ENVIRONMENT VARIABLES")
    print("=" * 40)
    
    env_vars = {
        'ES_CLUSTER_URL': os.environ.get('ES_CLUSTER_URL'),
        'ES_USERNAME': os.environ.get('ES_USERNAME'),
        'ES_PASSWORD': os.environ.get('ES_PASSWORD'),
        'ES_API_KEY': os.environ.get('ES_API_KEY'),
        'ES_INDEX': os.environ.get('ES_INDEX'),
    }
    
    for key, value in env_vars.items():
        if value:
            if key in ['ES_PASSWORD', 'ES_API_KEY']:
                print(f"✅ {key}: [SET - {len(value)} characters]")
            else:
                print(f"✅ {key}: {value}")
        else:
            print(f"❌ {key}: Not set")
    
    # Check which auth method is configured
    if env_vars['ES_API_KEY']:
        auth_method = 'api_key'
        print(f"\n🔑 Authentication: API Key")
    elif env_vars['ES_USERNAME'] and env_vars['ES_PASSWORD']:
        auth_method = 'username_password'
        print(f"\n🔑 Authentication: Username/Password")
    else:
        auth_method = 'none'
        print(f"\n❌ Authentication: No valid auth method detected")
    
    return {
        'env_vars': env_vars,
        'auth_method': auth_method,
        'cluster_url': env_vars['ES_CLUSTER_URL'],
        'index': env_vars['ES_INDEX'] or 'specialist-engagements'
    }

def test_config_module():
    """Test if the config module works with environment variables."""
    
    print(f"\n🧪 TESTING CONFIG MODULE")
    print("=" * 30)
    
    try:
        from config import get_elasticsearch_config_from_env, validate_es_config
        
        print("✅ Config module imported successfully")
        
        # Test getting config from environment
        es_config = get_elasticsearch_config_from_env()
        print(f"✅ Config extracted from environment")
        
        # Validate config
        is_valid, error_msg = validate_es_config(es_config)
        
        if is_valid:
            print(f"✅ Configuration is valid")
            print(f"   Cluster: {es_config.get('cluster_url', 'None')}")
            print(f"   Index: {es_config.get('index', 'None')}")
            print(f"   Auth: {es_config.get('auth_type', 'None')}")
            return es_config
        else:
            print(f"❌ Configuration validation failed: {error_msg}")
            return None
            
    except Exception as e:
        print(f"❌ Config module error: {str(e)}")
        return None

def test_elasticsearch_import():
    """Test if Elasticsearch library can be imported."""
    
    print(f"\n📦 TESTING ELASTICSEARCH IMPORT")
    print("=" * 35)
    
    try:
        from elasticsearch import Elasticsearch
        print("✅ Elasticsearch library imported successfully")
        
        # Try importing bulk helpers
        from elasticsearch.helpers import bulk
        print("✅ Elasticsearch helpers imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Elasticsearch import failed: {str(e)}")
        print("💡 Try: pip install elasticsearch --break-system-packages")
        return False

def test_elasticsearch_connection(es_config: Dict[str, Any]):
    """Test actual connection to Elasticsearch."""
    
    print(f"\n🔗 TESTING ELASTICSEARCH CONNECTION")
    print("=" * 40)
    
    try:
        from elasticsearch import Elasticsearch
        
        # Build connection parameters
        connection_params = {
            'verify_certs': False,
            'request_timeout': 30
        }
        
        if es_config.get('auth_type') == 'api_key':
            connection_params['api_key'] = es_config['api_key']
            print("🔑 Using API Key authentication")
        else:
            connection_params['basic_auth'] = (es_config['username'], es_config['password'])
            print("🔑 Using Username/Password authentication")
        
        print(f"🌐 Connecting to: {es_config['cluster_url']}")
        
        # Create connection
        es = Elasticsearch(
            [es_config['cluster_url']],
            **connection_params
        )
        
        # Test connection with cluster health
        print("🏥 Testing cluster health...")
        health = es.cluster.health()
        print(f"✅ Cluster connection successful!")
        print(f"   Cluster name: {health.get('cluster_name', 'Unknown')}")
        print(f"   Status: {health.get('status', 'Unknown')}")
        print(f"   Nodes: {health.get('number_of_nodes', 'Unknown')}")
        
        # Test cluster info
        print("\n📊 Testing cluster info...")
        info = es.info()
        print(f"✅ Cluster info retrieved!")
        print(f"   Version: {info.get('version', {}).get('number', 'Unknown')}")
        print(f"   Lucene: {info.get('version', {}).get('lucene_version', 'Unknown')}")
        
        return es
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        
        # Try to give specific error guidance
        error_str = str(e).lower()
        if 'authentication' in error_str or 'unauthorized' in error_str:
            print("💡 Authentication issue - check username/password or API key")
        elif 'connection' in error_str or 'timeout' in error_str:
            print("💡 Network issue - check cluster URL and network connectivity")
        elif 'ssl' in error_str or 'certificate' in error_str:
            print("💡 SSL issue - verify cluster URL (https vs http)")
        else:
            print("💡 Check cluster URL and credentials")
        
        return None

def test_index_operations(es, index_name: str):
    """Test index creation and operations."""
    
    print(f"\n📚 TESTING INDEX OPERATIONS")
    print("=" * 35)
    
    try:
        # Check if index exists
        if es.indices.exists(index=index_name):
            print(f"✅ Index '{index_name}' already exists")
            
            # Get index info
            index_info = es.indices.get(index=index_name)
            doc_count = es.count(index=index_name)['count']
            print(f"   Documents: {doc_count}")
            
        else:
            print(f"ℹ️  Index '{index_name}' does not exist yet")
            
            # Try to create a test index
            test_mapping = {
                "mappings": {
                    "properties": {
                        "test_field": {"type": "text"},
                        "timestamp": {"type": "date"}
                    }
                }
            }
            
            print(f"🔨 Creating test index...")
            es.indices.create(index=f"{index_name}_test", body=test_mapping)
            print(f"✅ Test index created successfully")
            
            # Clean up test index
            es.indices.delete(index=f"{index_name}_test")
            print(f"🧹 Test index cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Index operations failed: {str(e)}")
        return False

def test_document_indexing(es, index_name: str):
    """Test indexing a sample document."""
    
    print(f"\n📄 TESTING DOCUMENT INDEXING")
    print("=" * 35)
    
    try:
        # Create a test document
        test_doc = {
            'test_id': 'diagnostic_test_123',
            'message': 'Elasticsearch connection test',
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'es_diagnostics'
        }
        
        print("📝 Indexing test document...")
        
        # Index the document
        result = es.index(
            index=f"{index_name}_diagnostic_test",
            id='diagnostic_test_doc',
            body=test_doc
        )
        
        print(f"✅ Document indexed successfully!")
        print(f"   Result: {result.get('result', 'Unknown')}")
        print(f"   Index: {result.get('_index', 'Unknown')}")
        print(f"   ID: {result.get('_id', 'Unknown')}")
        
        # Wait for indexing
        es.indices.refresh(index=f"{index_name}_diagnostic_test")
        
        # Try to retrieve the document
        print("🔍 Retrieving test document...")
        retrieved = es.get(
            index=f"{index_name}_diagnostic_test",
            id='diagnostic_test_doc'
        )
        
        print(f"✅ Document retrieved successfully!")
        print(f"   Found: {retrieved.get('found', False)}")
        
        # Clean up test index
        es.indices.delete(index=f"{index_name}_diagnostic_test")
        print(f"🧹 Test index cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Document indexing failed: {str(e)}")
        return False

def test_bulk_indexing(es, index_name: str):
    """Test bulk indexing operations."""
    
    print(f"\n📦 TESTING BULK INDEXING")
    print("=" * 30)
    
    try:
        from elasticsearch.helpers import bulk
        
        # Create test documents
        test_docs = []
        for i in range(5):
            doc = {
                '_index': f"{index_name}_bulk_test",
                '_id': f'bulk_test_{i}',
                '_source': {
                    'doc_id': i,
                    'message': f'Bulk test document {i}',
                    'timestamp': datetime.utcnow().isoformat(),
                    'source': 'es_diagnostics_bulk'
                }
            }
            test_docs.append(doc)
        
        print(f"📦 Bulk indexing {len(test_docs)} documents...")
        
        # Perform bulk indexing
        success, failed = bulk(es, test_docs)
        
        print(f"✅ Bulk indexing completed!")
        print(f"   Successful: {success}")
        print(f"   Failed: {len(failed) if failed else 0}")
        
        if failed:
            print("❌ Some documents failed:")
            for failure in failed:
                print(f"   {failure}")
        
        # Verify documents
        es.indices.refresh(index=f"{index_name}_bulk_test")
        count_result = es.count(index=f"{index_name}_bulk_test")
        print(f"📊 Documents in test index: {count_result['count']}")
        
        # Clean up
        es.indices.delete(index=f"{index_name}_bulk_test")
        print(f"🧹 Test index cleaned up")
        
        return len(failed) == 0
        
    except Exception as e:
        print(f"❌ Bulk indexing failed: {str(e)}")
        return False

def main():
    """Main diagnostic function."""
    
    print("🔧 ELASTICSEARCH CONNECTION DIAGNOSTICS")
    print("=" * 50)
    print("This tool helps diagnose why data isn't reaching Elasticsearch")
    print()
    
    # Step 1: Check environment variables
    env_check = check_environment_variables()
    
    if not env_check['cluster_url']:
        print(f"\n❌ CRITICAL: ES_CLUSTER_URL not set")
        print("💡 Set it with: export ES_CLUSTER_URL='your_cluster_url'")
        return False
    
    if env_check['auth_method'] == 'none':
        print(f"\n❌ CRITICAL: No authentication method configured")
        print("💡 Set either:")
        print("   export ES_USERNAME='user' ES_PASSWORD='pass'")
        print("   OR")
        print("   export ES_API_KEY='your_api_key'")
        return False
    
    # Step 2: Test config module
    es_config = test_config_module()
    if not es_config:
        print(f"\n❌ CRITICAL: Config module failed")
        return False
    
    # Step 3: Test Elasticsearch import
    if not test_elasticsearch_import():
        return False
    
    # Step 4: Test ES connection
    es = test_elasticsearch_connection(es_config)
    if not es:
        print(f"\n❌ CRITICAL: Cannot connect to Elasticsearch")
        return False
    
    # Step 5: Test index operations
    index_name = es_config['index']
    if not test_index_operations(es, index_name):
        print(f"\n⚠️  WARNING: Index operations may have issues")
    
    # Step 6: Test document indexing
    if not test_document_indexing(es, index_name):
        print(f"\n❌ CRITICAL: Document indexing failed")
        return False
    
    # Step 7: Test bulk indexing
    if not test_bulk_indexing(es, index_name):
        print(f"\n⚠️  WARNING: Bulk indexing may have issues")
    
    print(f"\n🎉 DIAGNOSTICS COMPLETE")
    print("=" * 30)
    print("✅ All critical tests passed!")
    print("✅ Your Elasticsearch connection should work")
    print()
    print("🔍 NEXT STEPS:")
    print("1. Run your tool with verbose logging:")
    print("   python3 sf_account_opportunities.py --verbose 'account_url'")
    print()
    print("2. Check if you're using --json-only flag (which skips ES)")
    print()
    print("3. If still failing, run with debug:")
    print("   python3 debug_batch_sf_to_es.py your_file.txt")
    print()
    print("4. Check the logs for specific error messages")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n👋 Diagnostics cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)
