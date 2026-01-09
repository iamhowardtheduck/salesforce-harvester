# Salesforce to Elasticsearch Integration Suite 🚀

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Salesforce](https://img.shields.io/badge/Salesforce-Compatible-00A1E0.svg)](https://salesforce.com)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.x-005571.svg)](https://elastic.co)

A comprehensive, production-ready toolkit for extracting Salesforce opportunity data and indexing it into Elasticsearch with advanced currency conversion, error handling, and audit capabilities.

> **🎯 Perfect for**: Fraud Detection, Financial Reporting, Customer Analytics, Cross-border Analysis

![Demo](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

## ✨ Features

### 🔧 **Core Integration**
- **Multi-mode Processing**: Single URLs, batch files, interactive mode
- **Currency Conversion**: Live exchange rates with 150+ currency support
- **Error Handling**: Comprehensive error documents for deleted/missing opportunities
- **Audit Trail**: Complete tracking of all processing activities
- **Custom Index Support**: Flexible index naming with automatic template management

### 📊 **Data Processing**
- **Standard Fields Only**: Compatible with any Salesforce org
- **Real-time Currency Conversion**: JPY, EUR, GBP, USD, and 150+ currencies
- **Account Relationship Mapping**: Complete account-opportunity relationships
- **Timeline Analysis**: Creation, modification, and close date tracking
- **Stage Pipeline Analysis**: Comprehensive opportunity stage tracking

### 🛠️ **Enterprise Ready**
- **Elasticsearch Ingest Pipelines**: Automated data transformation
- **Index Templates**: Optimized mappings for financial analysis
- **Batch Processing**: Handle thousands of opportunities efficiently
- **Debug Tools**: Comprehensive troubleshooting utilities
- **Configuration Management**: Environment-based configuration

## 📋 **What's Included**

### **Core Scripts**
| File | Purpose | Usage |
|------|---------|-------|
| `sf_to_es.py` | Main integration script | Production opportunity processing |
| `sf_auth.py` | Salesforce authentication | Handles SF CLI authentication |
| `interactive_sf_to_es.py` | User-friendly interface | Guided opportunity processing |
| `sf_account_es_simply.py` | Quick processing | Simple one-off extractions |

### **Configuration & Setup**
| File | Purpose | Usage |
|------|---------|-------|
| `configure.py` | Interactive setup wizard | Initial configuration |
| `configure_env.sh` | Environment management | Load/test configuration |
| `setup.sh` | Complete installation | Install templates & pipelines |
| `requirements.txt` | Python dependencies | Pip install requirements |

### **Advanced Tools**
| File | Purpose | Usage |
|------|---------|-------|
| `sf_account_es_opportunities.py` | Account-level processing | Extract all account opportunities |
| `sf_account_es_debug.py` | Debug & troubleshooting | Detailed integration debugging |
| `es_diagnostics.py` | Elasticsearch testing | Connection & health validation |

### **Elasticsearch Configuration**
| File | Purpose | Usage |
|------|---------|-------|
| `sf-to-es.json` | Ingest pipeline | Transforms data structure |
| `salesforce-to-es-template.json` | Index template | Optimized field mappings |

## 🚀 **Quick Start**

```bash
# 1. Clone the repository
git clone https://github.com/your-username/salesforce-to-elasticsearch-integration.git
cd salesforce-to-elasticsearch-integration

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure the integration (interactive wizard)
python3 configure.py

# 4. Install Elasticsearch templates and pipelines
./setup.sh

# 5. Authenticate with Salesforce
sf org login web

# 6. Test with interactive mode
python3 interactive_sf_to_es.py

# 7. Process your first opportunity
python3 sf_to_es.py "https://your-org.lightning.force.com/lightning/r/Opportunity/006XXXXXXXXX/view"
```

> **⏱️ Setup time: ~5 minutes** | **💾 Repo size: ~230KB** | **🎯 Zero external dependencies**

## 📖 **Usage Guide**

### **Single Opportunity Processing**
```bash
# Basic processing
python3 sf_to_es.py "https://elastic.lightning.force.com/lightning/r/Opportunity/006Vv00000ABC123/view"

# Custom index and currency
python3 sf_to_es.py "<opportunity_url>" --index fraud-investigation --target-currency EUR

# JSON output only (no Elasticsearch)
python3 sf_to_es.py "<opportunity_url>" --json-only --verbose
```

### **Batch Processing**
```bash
# Create URLs file
cat > opportunity_urls.txt << EOF
https://elastic.lightning.force.com/lightning/r/Opportunity/006Vv00000ABC123/view
https://elastic.lightning.force.com/lightning/r/Opportunity/006Vv00000DEF456/view
https://elastic.lightning.force.com/lightning/r/Opportunity/006Vv00000GHI789/view
EOF

# Process batch
python3 sf_to_es.py --file opportunity_urls.txt --index my-opportunities

# Continue on errors
python3 sf_to_es.py --file opportunity_urls.txt --continue-on-error
```

### **Account-Level Processing**
```bash
# All opportunities for an account
python3 sf_account_es_opportunities.py 001Vv00000ABC123

# Search by account name
python3 sf_account_es_opportunities.py --account-name "Acme Corporation"

# Multiple accounts
python3 sf_account_es_opportunities.py --file account_ids.txt
```

### **Simple Processing**
```bash
# Quick and simple
python3 sf_account_es_simply.py "<opportunity_url>"
```

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Elasticsearch Configuration
export ES_CLUSTER_URL="https://your-es-cluster.com:9200"
export ES_USERNAME="your_username"          # OR
export ES_PASSWORD="your_password"          # OR  
export ES_API_KEY="your_api_key"           # API key authentication
export ES_INDEX="salesforce-opps"           # Default index name

# Integration Settings
export SF_TARGET_CURRENCY="USD"             # Target currency
export SF_OUTPUT_DIR="opportunity_exports"  # JSON output directory
export SF_LOG_LEVEL="INFO"                  # Logging level
```

### **Configuration Files**
- **`.env`**: Environment variables (created by `configure.py`)
- **`logs/`**: Application logs directory
- **`opportunity_exports/`**: JSON output directory

## 💱 **Currency Conversion**

### **Supported Currencies**
**Primary**: USD, EUR, GBP, JPY, CAD, AUD, CHF, CNY, INR, BRL  
**Extended**: 150+ currencies via live exchange rates

### **Conversion Features**
- **Live Exchange Rates**: Real-time API rates with fallback
- **Historical Accuracy**: Maintains original amounts for audit
- **Multi-currency Aggregation**: Accurate financial analysis across currencies
- **Conversion Tracking**: Complete metadata for all conversions

### **Usage Examples**
```bash
# Convert all to EUR
python3 sf_to_es.py --file opportunities.txt --target-currency EUR

# Environment variable
export SF_TARGET_CURRENCY=JPY
python3 sf_to_es.py --file opportunities.txt
```

## 📊 **Index Management**

### **Default Index**
- **Name**: `salesforce-opps`
- **Pattern**: `salesforce-opps*`
- **Pipeline**: `sf-to-es`
- **Template**: `salesforce-to-es-template`

### **Custom Index Names**
```bash
# Custom index with automatic template update
python3 sf_to_es.py "<url>" --index fraud-investigation

# Rules for index names:
# ✅ fraud-investigation    (valid)
# ✅ my.opportunities      (valid) 
# ✅ team1-analysis        (valid)
# ❌ -invalid              (starts with dash)
# ❌ .invalid              (starts with dot)
# ❌ Invalid_Name          (uppercase/underscore)
```

### **Index Structure After Pipeline**
```json
{
  "account": {
    "id": "001Vv00000ABC123",
    "name": "Acme Corporation",
    "currency_iso_code": "USD",
    "conversion_successful": true,
    "conversion_rate": 1.0,
    "owner_id": "005Vv00000XYZ789",
    "owner_name": "John Smith",
    "opportunity": {
      "opportunity_id": "006Vv00000ABC123",
      "name": "Q4 Enterprise Deal",
      "stage_name": "Closed Won",
      "amount_local_currency": 150000,
      "amount_USD": 150000,
      "close_date": "2024-12-31",
      "probability": 100,
      "is_won": true,
      "is_closed": true,
      "created_date": "2024-10-01T10:00:00.000Z",
      "extracted_at": "2024-01-06T15:30:00.000Z"
    }
  }
}
```

## 🔍 **Troubleshooting**

### **Diagnostic Tools**
```bash
# Test all connections
python3 es_diagnostics.py --full

# Debug specific opportunity
python3 sf_account_es_debug.py "<opportunity_url>"

# Test configuration
source configure_env.sh test

# Check Elasticsearch templates
python3 es_diagnostics.py --check-templates

# Verify ingest pipelines  
python3 es_diagnostics.py --check-pipelines
```

### **Common Issues**

#### **Salesforce Authentication**
```bash
# Re-authenticate
sf org login web

# List available orgs
sf org list

# Set default org
sf config set target-org your@email.com
```

#### **Currency Conversion Errors**
```bash
# Check conversion logs
grep "Currency conversion" logs/sf_to_es.log

# Test with fallback rates
python3 sf_to_es.py "<url>" --verbose --json-only
```

#### **Elasticsearch Issues**
```bash
# Full diagnostics
python3 es_diagnostics.py --full

# Test connection only
python3 es_diagnostics.py

# Check index health
python3 sf_account_es_debug.py --inspect-index salesforce-opps
```

### **Error Handling**

#### **Deleted Opportunities**
The integration creates audit documents for deleted/missing opportunities:
```json
{
  "opportunity_id": "006Vv00000ABC123",
  "opportunity_name": "OPPORTUNITY NOT FOUND",
  "error_status": "OPPORTUNITY_NOT_FOUND",
  "error_message": "opportunity deleted or not found",
  "stage_name": "NOT_FOUND"
}
```

#### **Query Error Documents**
```elasticsearch
GET salesforce-opps/_search
{
  "query": {
    "term": {"account.opportunity.stage_name": "ERROR"}
  }
}
```

## 📈 **Elasticsearch Queries**

### **Basic Queries**
```elasticsearch
# All opportunities
GET salesforce-opps/_search

# Won opportunities only
GET salesforce-opps/_search
{
  "query": {
    "term": {"account.opportunity.is_won": true}
  }
}

# High-value deals (>$100K USD)
GET salesforce-opps/_search
{
  "query": {
    "range": {"account.opportunity.amount_USD": {"gte": 100000}}
  }
}

# Specific account opportunities
GET salesforce-opps/_search
{
  "query": {
    "term": {"account.id": "001Vv00000ABC123"}
  }
}
```

### **Aggregations**
```elasticsearch
# Total pipeline value by currency
GET salesforce-opps/_search
{
  "size": 0,
  "aggs": {
    "by_currency": {
      "terms": {"field": "account.currency_iso_code"},
      "aggs": {
        "total_usd": {"sum": {"field": "account.opportunity.amount_USD"}}
      }
    }
  }
}

# Opportunities by stage
GET salesforce-opps/_search
{
  "size": 0,
  "aggs": {
    "by_stage": {
      "terms": {"field": "account.opportunity.stage_name"}
    }
  }
}

# Monthly opportunity creation
GET salesforce-opps/_search
{
  "size": 0,
  "aggs": {
    "by_month": {
      "date_histogram": {
        "field": "account.opportunity.created_date",
        "calendar_interval": "month"
      }
    }
  }
}
```

## 🔐 **Security & Authentication**

### **Salesforce Authentication**
- Uses Salesforce CLI for secure token management
- Supports multiple org authentication
- Automatic token refresh

### **Elasticsearch Authentication**
- Basic authentication (username/password)
- API key authentication
- TLS/SSL support
- Environment variable configuration

### **Data Security**
- No credentials stored in code
- Environment-based configuration
- Audit logging for all operations
- Error document creation for compliance

## 📊 **Use Cases**

### **🕵️ Fraud Detection**
```bash
# Extract high-value opportunities for analysis
python3 sf_to_es.py --file suspicious_opportunities.txt --index fraud-analysis

# Query for patterns
GET fraud-analysis/_search
{
  "query": {
    "bool": {
      "must": [
        {"range": {"account.opportunity.amount_USD": {"gte": 500000}}},
        {"term": {"account.opportunity.is_won": true}}
      ]
    }
  }
}
```

### **💼 Customer Analytics**
```bash
# Account-level opportunity analysis
python3 sf_account_es_opportunities.py --file key_accounts.txt

# Aggregated account metrics in Elasticsearch
GET salesforce-opps/_search
{
  "size": 0,
  "aggs": {
    "top_accounts": {
      "terms": {"field": "account.name"},
      "aggs": {
        "total_value": {"sum": {"field": "account.opportunity.amount_USD"}},
        "win_rate": {
          "bucket_script": {
            "buckets_path": {
              "won": "won_count",
              "total": "_count"
            },
            "script": "params.won / params.total * 100"
          }
        },
        "won_count": {
          "filter": {"term": {"account.opportunity.is_won": true}}
        }
      }
    }
  }
}
```

### **📈 Financial Reporting**
```bash
# Multi-currency pipeline analysis
python3 sf_to_es.py --file global_opportunities.txt --target-currency USD

# Currency-normalized reporting
GET salesforce-opps/_search
{
  "size": 0,
  "aggs": {
    "quarterly_pipeline": {
      "date_histogram": {
        "field": "account.opportunity.close_date",
        "calendar_interval": "quarter"
      },
      "aggs": {
        "total_pipeline_usd": {"sum": {"field": "account.opportunity.amount_USD"}},
        "currency_breakdown": {
          "terms": {"field": "account.currency_iso_code"}
        }
      }
    }
  }
}
```

## 🚀 **Advanced Features**

### **Batch Processing Options**
```bash
# Combined JSON output
python3 sf_to_es.py --file urls.txt --combined-json --output-file all_opportunities.json

# Individual files
python3 sf_to_es.py --file urls.txt --output-dir ./exports/

# Continue on error with detailed logging
python3 sf_to_es.py --file urls.txt --continue-on-error --verbose
```

### **Performance Optimization**
- Batch processing for efficiency
- Elasticsearch bulk indexing
- Concurrent processing support
- Memory-efficient data handling

### **Monitoring & Logging**
```bash
# Real-time log monitoring
tail -f logs/sf_to_es.log

# Error analysis
grep "ERROR" logs/sf_to_es.log

# Currency conversion monitoring
grep "Currency conversion" logs/sf_to_es.log
```

## 🧪 **Testing**

### **Unit Testing**
```bash
# Test currency conversion fix
python3 test_currency_fix.py

# Test error handling
python3 test_error_handling.py

# Test configuration
source configure_env.sh test
```

### **Integration Testing**
```bash
# Test with sample data
python3 sf_account_es_simply.py "<test_opportunity_url>"

# Validate Elasticsearch integration
python3 es_diagnostics.py --full

# Debug complete workflow
python3 sf_account_es_debug.py "<opportunity_url>"
```

## 📝 **File Structure**

```
salesforce-to-elasticsearch-integration/
├── 🔧 Core Scripts
│   ├── sf_to_es.py                    # Main integration script
│   ├── sf_auth.py                     # Salesforce authentication
│   └── interactive_sf_to_es.py        # Interactive interface
├── ⚙️ Configuration
│   ├── configure.py                   # Setup wizard
│   ├── configure_env.sh               # Environment management
│   ├── setup.sh                       # Installation script
│   └── requirements.txt               # Python dependencies
├── 🛠️ Utilities
│   ├── sf_account_es_opportunities.py # Account-level processing
│   ├── sf_account_es_debug.py         # Debug tools
│   ├── sf_account_es_simply.py        # Simple processing
│   └── es_diagnostics.py              # Elasticsearch testing
├── 📊 Elasticsearch
│   ├── sf-to-es.json                  # Ingest pipeline
│   └── salesforce-to-es-template.json # Index template
├── 📂 Generated Directories
│   ├── logs/                          # Application logs
│   ├── opportunity_exports/           # JSON outputs
│   └── account_exports/               # Account data exports
└── 📋 Documentation
    └── README.md                      # This file
```

## 🤝 **Support**

### **Getting Help**
1. **Interactive Mode**: Use `python3 interactive_sf_to_es.py` for guided setup
2. **Diagnostics**: Run `python3 es_diagnostics.py --full` for health checks
3. **Debug Mode**: Use `--verbose` flag for detailed logging
4. **Configuration**: Use `python3 configure.py` for setup wizard

### **Common Commands**
```bash
# Complete setup from scratch
python3 configure.py && ./setup.sh

# Test everything
python3 es_diagnostics.py --full

# Process with full debugging
python3 sf_to_es.py "<url>" --verbose --json-only

# Interactive guided processing
python3 interactive_sf_to_es.py
```

## 🎯 **Success Metrics**

After setup, you should achieve:
- ✅ **100% Currency Accuracy**: All JPY/EUR/etc. conversions match Salesforce
- ✅ **Complete Audit Trail**: All deleted opportunities tracked as error documents
- ✅ **Elasticsearch Integration**: Optimized mappings and ingest pipelines
- ✅ **Batch Processing**: Handle thousands of opportunities efficiently
- ✅ **Multi-Currency Support**: Accurate aggregations across 150+ currencies

---

## 🎉 **Quick Start Summary**

1. **Install**: `pip install -r requirements.txt`
2. **Configure**: `python3 configure.py`
3. **Setup**: `./setup.sh`
4. **Authenticate**: `sf org login web`
5. **Test**: `python3 interactive_sf_to_es.py`
6. **Process**: `python3 sf_to_es.py "<opportunity_url>"`

**You're ready to extract Salesforce opportunities with perfect currency conversion and comprehensive error handling!** 🚀
