# Salesforce to Elasticsearch Integration Toolkit 🚀

A comprehensive toolkit for extracting, analyzing, and indexing Salesforce data (opportunities, cases, accounts) into Elasticsearch. Purpose-built for data analysis, fraud detection, compliance reporting, and business intelligence workflows.

## ✨ **What This Toolkit Does**

- **📊 Opportunity Analysis** - Extract and analyze sales opportunities with account relationships
- **📞 Case Investigation** - Retrieve support cases with investigation notes and comments
- **🏢 Account Intelligence** - Account-specific analysis across opportunities and cases
- **🔍 Cross-Reference Analysis** - Link opportunities, cases, and accounts for complete customer view
- **📈 Sales Performance** - Closed deals analysis, win rates, revenue tracking, executive dashboards
- **🚨 Compliance & Fraud** - Pattern detection, audit trails, investigation timelines
- **⚡ Elasticsearch Integration** - Bulk indexing with proper mappings for advanced analytics

## 🎯 **Perfect for Your Workflows**

- **💼 Sales Intelligence** - Performance analytics, account health, pipeline analysis
- **🎫 Support Operations** - Case management, resolution tracking, escalation patterns
- **📈 Executive Reporting** - Real-time dashboards, trend analysis, performance metrics

---

## 🚀 **Quick Start**

### **1. Setup (One-Time)**
```bash
# Clone or download the toolkit
git clone https://github.com/iamhowardtheduck/salesforce-harvester.git
cd salesforce-harvester

# Run automated setup
chmod +x setup.sh
./setup.sh

# Configure Elasticsearch (optional - can be done interactively)
chmod +x configure_env.sh
./configure_env.sh
```

### **2. Test Salesforce Connection**
```bash
# Authenticate with Salesforce (one-time)
sf org login web -r https://your-org.my.salesforce.com

# Quick test (no Elasticsearch needed)
python3 sf_to_json.py "your_opportunity_url"
```

### **3. Test Elasticsearch Connection**
```bash
# Diagnostic test
python3 es_diagnostics.py

# Or set environment variables
export ES_CLUSTER_URL="https://your-cluster.es.example.com"
export ES_USERNAME="your_username"
export ES_PASSWORD="your_password"
export ES_INDEX="salesforce-data"
```

### **4. Start Analyzing**
```bash
# Quick sales analysis
python3 sf_closed_simple.py

# Account investigation
python3 sf_account_simple.py "account_url"

# Case management
python3 sf_cases_simple.py --priority High

# Full Elasticsearch integration
python3 sf_closed_opportunities.py
python3 sf_cases_to_elasticsearch.py
```

---

## 🛠️ **All Available Tools**

### **📊 Core Opportunity Processing**
| Tool | Purpose | Output | Use Case |
|------|---------|--------|----------|
| `sf_to_elasticsearch.py` | Single opportunity → ES | Elasticsearch | Individual deal analysis |
| `batch_sf_to_elasticsearch.py` | Multiple opportunities → ES | Elasticsearch | Bulk opportunity processing |
| `interactive_sf_to_es.py` | Menu-driven interface | Interactive/ES | User-friendly operation |

**Usage:**
```bash
# Single opportunity
python3 sf_to_elasticsearch.py "opportunity_url"

# Multiple opportunities from file
python3 batch_sf_to_elasticsearch.py opportunity_urls.txt

# Interactive interface
python3 interactive_sf_to_es.py
```

### **📋 JSON Testing & Exploration**
| Tool | Purpose | Output | Use Case |
|------|---------|--------|----------|
| `sf_to_json.py` | Simple opportunity export | JSON | Quick testing, field verification |
| `sf_explore_json.py` | Field discovery | JSON | Explore available fields in your org |

**Usage:**
```bash
# Quick test (no ES required)
python3 sf_to_json.py "opportunity_url"

# Discover all available fields
python3 sf_explore_json.py "opportunity_url"
```

### **📈 Sales Performance Analysis**
| Tool | Purpose | Output | Use Case |
|------|---------|--------|----------|
| `sf_closed_opportunities.py` | Complete closed deals analysis | ES + JSON | Sales performance, revenue analysis |
| `sf_closed_simple.py` | Quick sales metrics | JSON | Rapid sales insights |
| `sf_sales_dashboard.py` | Real-time sales dashboard | Live Display | Executive reporting |

**Usage:**
```bash
# Complete sales analysis to Elasticsearch
python3 sf_closed_opportunities.py

# Quick sales overview
python3 sf_closed_simple.py --won-only

# Live sales dashboard
python3 sf_sales_dashboard.py

# Specific date range
python3 sf_closed_opportunities.py --date-from 2024-01-01 --date-to 2024-12-31
```

### **🏢 Account Intelligence**
| Tool | Purpose | Output | Use Case |
|------|---------|--------|----------|
| `sf_account_opportunities.py` | Account opportunities analysis | ES + JSON | Account health, relationship analysis |
| `sf_account_simple.py` | Quick account overview | JSON | Fast account insights |

**Usage:**
```bash
# Single account analysis
python3 sf_account_opportunities.py "account_url"

# Multiple accounts
python3 sf_account_opportunities.py "url1" "url2" "url3"

# Accounts from file
python3 sf_account_opportunities.py --accounts-file key_accounts.txt

# Quick account check
python3 sf_account_simple.py "account_url"
```

### **📞 Case Management & Investigation**
| Tool | Purpose | Output | Use Case |
|------|---------|--------|----------|
| `sf_cases_to_elasticsearch.py` | All cases + comments → ES | ES + JSON | Investigation, compliance tracking |
| `sf_cases_simple.py` | Quick case analysis | JSON | Support metrics, case overview |
| `sf_account_cases.py` | Account-specific cases | ES + JSON | Customer issue tracking |
| `sf_account_cases_simple.py` | Quick account case view | JSON | Fast account support history |
| `sf_account_cases_analysis.py` | Advanced case analytics | ES + JSON | Case trends, patterns |
| `sf_opportunity_cases.py` | Opportunity + case integration | ES + JSON | Complete customer journey |
| `sf_all_cases_simple.py` | Organization-wide cases | JSON | Department metrics |

**Usage:**
```bash
# All cases to Elasticsearch
python3 sf_cases_to_elasticsearch.py --with-comments

# High priority cases only
python3 sf_cases_to_elasticsearch.py --priority High,Critical --open-only

# Account case investigation
python3 sf_account_cases.py "account_url" --with-comments

# Quick case overview
python3 sf_cases_simple.py --limit 50

# Complete customer view (opportunities + cases)
python3 sf_opportunity_cases.py --account-analysis "account_url"
```

### **🔧 Debug & Troubleshooting**
| Tool | Purpose | Output | Use Case |
|------|---------|--------|----------|
| `es_diagnostics.py` | ES connection testing | Diagnostic | Troubleshoot ES issues |
| `tool_checker.py` | Tool usage verification | Diagnostic | Identify tool problems |
| `account_debug.py` | Account-specific debugging | Diagnostic | Debug account data issues |
| `debug_batch_sf_to_es.py` | Debug batch processing | Debug logs | Troubleshoot batch issues |
| `verify_soql.py` | Query verification | SOQL display | Verify queries before execution |

**Usage:**
```bash
# Test Elasticsearch connection
python3 es_diagnostics.py

# Check which tools you're using
python3 tool_checker.py

# Debug account with no data
python3 account_debug.py "account_url"

# Debug batch processing
python3 debug_batch_sf_to_es.py urls.txt

# Verify SOQL queries
python3 verify_soql.py "opportunity_url"
```

---

## ⚙️ **Configuration**

### **Salesforce Authentication**
```bash
# One-time setup
sf org login web -r https://your-org.my.salesforce.com

# Verify connection
sf org display
```

### **Elasticsearch Configuration**

**Option 1: Environment Variables (Recommended)**
```bash
export ES_CLUSTER_URL="https://your-cluster.es.example.com"
export ES_USERNAME="your_username"
export ES_PASSWORD="your_password"
export ES_INDEX="salesforce-data"
```

**Option 2: API Key Authentication (More Secure)**
```bash
export ES_CLUSTER_URL="https://your-cluster.es.example.com" 
export ES_API_KEY="your_base64_encoded_api_key"
export ES_INDEX="salesforce-data"
```

**Option 3: Interactive Configuration**
```bash
./configure_env.sh
```

**Option 4: Runtime Prompts**
Most tools will prompt for ES configuration if environment variables aren't set.

### **Index Configuration**
```bash
# Single index for all data (simple)
export ES_INDEX="salesforce-data"

# Separate indices by data type (organized)
export ES_OPPORTUNITIES_INDEX="opportunities"
export ES_ACCOUNT_INDEX="account-opportunities"
export ES_CASES_INDEX="cases"
export ES_CLOSED_INDEX="closed-opportunities"
```

---

## 🎯 **Common Use Cases**

### **1. Sales Performance Analysis**
```bash
# Quick sales overview
python3 sf_closed_simple.py --won-only

# Complete sales analysis to ES
python3 sf_closed_opportunities.py --date-from 2024-01-01

# Real-time sales dashboard
python3 sf_sales_dashboard.py

# Account performance comparison
python3 sf_account_opportunities.py --accounts-file top_accounts.txt
```

### **2. Account Intelligence & Health**
```bash
# Account relationship analysis
python3 sf_account_opportunities.py "account_url"

# Account support history
python3 sf_account_cases.py "account_url" --with-comments

# Complete account view (sales + support)
python3 sf_opportunity_cases.py --account-analysis "account_url"

# Multiple account comparison
python3 sf_account_simple.py --file strategic_accounts.txt
```

### **3. Case Management & Investigation**
```bash
# Investigation case tracking
python3 sf_cases_to_elasticsearch.py --priority High,Critical --with-comments

# Support performance metrics
python3 sf_cases_simple.py

# Account issue patterns
python3 sf_account_cases_analysis.py "account_url"

# Organization-wide case trends
python3 sf_all_cases_simple.py
```

### **4. Fraud Detection & AML Compliance**
```bash
# Account investigation workflow
python3 sf_account_simple.py "suspicious_account_url"
python3 sf_account_cases.py "suspicious_account_url" --priority High --with-comments
python3 sf_opportunity_cases.py --account-analysis "suspicious_account_url"

# Pattern analysis across accounts
python3 sf_closed_opportunities.py --json-only > sales_patterns.json
python3 sf_cases_to_elasticsearch.py --priority High,Critical

# Compliance audit trail
python3 sf_cases_to_elasticsearch.py --date-from 2024-01-01 --with-comments
```

### **5. Executive Reporting**
```bash
# Real-time dashboard
python3 sf_sales_dashboard.py --one-time

# Monthly sales report
python3 sf_closed_opportunities.py --date-from 2024-12-01 --json-only

# Support performance report
python3 sf_cases_simple.py --date-from 2024-12-01

# Account health report
python3 sf_account_opportunities.py --accounts-file vip_accounts.txt --json-only
```

### **6. Data Migration & Bulk Processing**
```bash
# Bulk opportunity migration
python3 batch_sf_to_elasticsearch.py all_opportunities.txt

# Historical data migration
python3 sf_closed_opportunities.py --date-from 2020-01-01

# Complete data integration
python3 sf_cases_to_elasticsearch.py --with-comments
python3 sf_closed_opportunities.py
```

---

## 📊 **Data Structure & Schema**

### **Opportunity Data**
```json
{
  "opportunity_id": "006Vv00000IZaFxIAL",
  "opportunity_name": "Enterprise Security Platform",
  "account_id": "001b000000kFpsaAAC",
  "account_name": "Acme Corporation",
  "close_date": "2024-12-15",
  "amount": 500000.00,
  "stage_name": "Closed Won",
  "is_won": true,
  "type": "New Business",
  "probability": 100,
  "owner_name": "John Smith",
  "created_date": "2024-06-15T10:30:00.000+0000",
  "extracted_at": "2025-12-09T20:45:30.123456",
  "source": "salesforce_opportunities"
}
```

### **Case Data with Comments**
```json
{
  "case_id": "500b000000ABC123",
  "case_number": "00001234",
  "subject": "Login Issues",
  "description": "Customer cannot access account",
  "status": "Investigating",
  "priority": "High",
  "type": "Problem",
  "created_date": "2024-12-09T10:30:00.000+0000",
  "is_closed": false,
  "account_id": "001b000000kFpsaAAC",
  "account_name": "Acme Corporation",
  "owner_name": "Support Agent",
  "comments_count": 3,
  "case_comments": [
    {
      "comment_id": "00ab000000XYZ789",
      "comment_body": "Investigated issue. Password reset required.",
      "created_date": "2024-12-09T11:00:00.000+0000",
      "created_by_name": "Support Agent",
      "is_published": true
    }
  ],
  "extracted_at": "2025-12-09T20:45:30.123456",
  "source": "salesforce_cases"
}
```

### **Elasticsearch Index Mappings**
The toolkit automatically creates optimized Elasticsearch mappings for:
- **Date range filtering** (creation, close, modification dates)
- **Keyword aggregations** (status, stage, priority, type, subjects, descriptions, names)
- **Numeric analysis** (amounts, probabilities, counts)
- **Nested objects** (case comments, account relationships)
- **Boolean filtering** (won/lost, open/closed, escalated)

---

## 🔍 **Advanced Features**

### **Filtering & Date Ranges**
```bash
# Date filtering
--date-from 2024-01-01 --date-to 2024-12-31

# Status filtering  
--open-only --closed-only --won-only --lost-only

# Priority filtering
--priority High,Critical

# Limit results
--limit 100
```

### **Output Options**
```bash
# Elasticsearch integration (default)
python3 sf_closed_opportunities.py

# JSON output only (no ES)
python3 sf_closed_opportunities.py --json-only

# Custom output file
python3 sf_closed_opportunities.py --output-file my_analysis.json

# Verbose logging
python3 sf_closed_opportunities.py --verbose
```

### **Bulk Processing**
```bash
# Create URL files
echo "opportunity_url_1" > opportunities.txt
echo "opportunity_url_2" >> opportunities.txt

# Process in bulk
python3 batch_sf_to_elasticsearch.py opportunities.txt

# Account file processing
echo "account_url_1" > accounts.txt
python3 sf_account_opportunities.py --accounts-file accounts.txt
```

---

## 🚨 **Troubleshooting**

### **Quick Diagnostics**
```bash
# Test all connections
python3 es_diagnostics.py

# Check tool usage
python3 tool_checker.py

# Debug specific account
python3 account_debug.py "account_url"
```

### **Common Issues**

**1. No Data in Elasticsearch (Index Created)**
```bash
# Most common cause: Using JSON-only tools or --json-only flag
# Solution: Use ES-enabled tools without --json-only
python3 sf_closed_opportunities.py  # ✅ Uses ES
python3 sf_closed_simple.py         # ❌ JSON only

# Check if account has closed opportunities
python3 account_debug.py "account_url"
```

**2. Elasticsearch Connection Issues**
```bash
# Test connection
python3 es_diagnostics.py

# Check environment variables
echo $ES_CLUSTER_URL
echo $ES_USERNAME

# Test with curl
curl -X GET "$ES_CLUSTER_URL/_cluster/health" -u "$ES_USERNAME:$ES_PASSWORD"
```

**3. Salesforce Authentication**
```bash
# Re-authenticate
sf org login web -r https://your-org.my.salesforce.com

# Test connection
python3 sf_to_json.py "opportunity_url"
```

**4. Import/Module Errors**
```bash
# Test setup
python3 test_validation.py

# Reinstall dependencies
pip install simple-salesforce elasticsearch requests --break-system-packages
```

### **Debug Tools**
- `es_diagnostics.py` - Test Elasticsearch connection step-by-step
- `tool_checker.py` - Identify which tools you're using and their ES support  
- `account_debug.py` - Debug account opportunities with no data
- `debug_batch_sf_to_es.py` - Debug batch processing issues
- `verify_soql.py` - Verify SOQL queries without execution

---

## 📖 **Documentation**

### **Complete Guides**
- [CLOSED_OPPORTUNITIES_GUIDE.md](CLOSED_OPPORTUNITIES_GUIDE.md) - Sales performance analysis
- [ACCOUNT_OPPORTUNITIES_GUIDE.md](ACCOUNT_OPPORTUNITIES_GUIDE.md) - Account intelligence  
- [CASES_TOOLKIT_GUIDE.md](CASES_TOOLKIT_GUIDE.md) - Case management & investigation
- [ELASTICSEARCH_ACCOUNT_CONFIG.md](ELASTICSEARCH_ACCOUNT_CONFIG.md) - ES configuration

### **Troubleshooting Guides**
- [ES_DATA_NOT_APPEARING_FIX.md](ES_DATA_NOT_APPEARING_FIX.md) - Fix data not appearing in ES
- [ACCOUNT_NO_DATA_FIX.md](ACCOUNT_NO_DATA_FIX.md) - Fix account tools creating index but no data
- [TCV_TROUBLESHOOTING.md](TCV_TROUBLESHOOTING.md) - Complete troubleshooting guide

### **Setup Guides**  
- [SETUP_SCRIPTS_UPDATE.md](SETUP_SCRIPTS_UPDATE.md) - Updated setup and configuration
- [FILE_LISTING.md](FILE_LISTING.md) - Complete file overview

---

## 💡 **Tips & Best Practices**

### **Getting Started**
1. **Start with JSON tools** for testing (no ES setup required)
2. **Use simple tools** for quick insights  
3. **Move to ES integration** for production analytics
4. **Test with diagnostic tools** when issues arise

### **Production Use**
1. **Use environment variables** for automation
2. **Set up proper ES indices** for data organization  
3. **Use API keys** instead of username/password for security
4. **Monitor ES cluster health** during bulk imports
5. **Use date filtering** for incremental updates

### **Data Organization**
1. **Consistent field names** across all ES indices
2. **Tag documents** with source field for data lineage
3. **Include extracted_at** timestamps for audit trails
4. **Use meaningful index names** (e.g., `opportunities-2024`)

### **Performance**
1. **Use bulk indexing** (already implemented in tools)
2. **Set appropriate refresh intervals** for your use case
3. **Monitor cluster health** during large imports
4. **Consider date-based indices** for time series data

---

## 📈 **Integration Examples**

### **Kibana Dashboard Queries**

**Sales Performance by Account:**
```json
{
  "query": {
    "bool": {
      "must": [
        {"term": {"is_won": true}},
        {"range": {"close_date": {"gte": "2024-01-01"}}}
      ]
    }
  },
  "aggs": {
    "by_account": {
      "terms": {"field": "account_name.keyword"},
      "aggs": {
        "total_revenue": {"sum": {"field": "amount"}}
      }
    }
  }
}
```

**Case Investigation Timeline:**
```json
{
  "query": {
    "bool": {
      "must": [
        {"term": {"priority": "High"}},
        {"term": {"account_id": "001b000000kFpsaAAC"}}
      ]
    }
  },
  "aggs": {
    "timeline": {
      "date_histogram": {
        "field": "created_date",
        "calendar_interval": "week"
      }
    }
  }
}
```

### **Python Analysis Scripts**
```python
# Connect to Elasticsearch
from elasticsearch import Elasticsearch
es = Elasticsearch(["https://your-cluster.com"], ...)

# Cross-reference opportunities and cases
def analyze_account_health(account_id):
    # Get opportunities
    opp_query = {"query": {"term": {"account_id": account_id}}}
    opportunities = es.search(index="opportunities", body=opp_query)
    
    # Get cases  
    case_query = {"query": {"term": {"account_id": account_id}}}
    cases = es.search(index="cases", body=case_query)
    
    # Analyze patterns
    return {
        "revenue": sum(o["_source"]["amount"] for o in opportunities["hits"]["hits"]),
        "case_count": cases["hits"]["total"]["value"],
        "high_priority_cases": len([c for c in cases["hits"]["hits"] 
                                   if c["_source"]["priority"] == "High"])
    }
```

---

---

## 🤝 **Contributing & Support**

### **Extending the Toolkit**
The toolkit is designed to be extensible:
- **Add new Salesforce objects** by following the existing pattern
- **Create custom analytics** using the ES data structure  
- **Build custom dashboards** with Kibana or your preferred tool
- **Integrate with other systems** using the JSON export functionality

### **Configuration Files**
All configuration is handled through:
- **Environment variables** for automation
- **Interactive prompts** for manual setup
- **Configuration files** generated by `configure_env.sh`
- **Runtime detection** with fallback options

---

## ✨ **Ready to Start**

The toolkit is production-ready with comprehensive error handling, extensive documentation, and diagnostic tools for troubleshooting. Your fraud detection and AML compliance workflows will immediately benefit from the integrated case investigation capabilities and cross-reference analysis features.

**Start here:**
```bash
./setup.sh
python3 sf_closed_simple.py
```

**Then explore:**
```bash
python3 sf_account_simple.py "account_url"
python3 sf_cases_simple.py --priority High
```

**Finally, integrate:**
```bash
python3 sf_closed_opportunities.py
python3 sf_cases_to_elasticsearch.py --with-comments
```

Happy analyzing! 🎯

## Configuration

The tool uses interactive configuration prompts to gather your Elasticsearch settings. When you run any script, you'll be prompted for:

### Elasticsearch Settings:
- **Cluster URL**: Your Elasticsearch cluster endpoint
- **Index Name**: Target index (defaults to "specialist-engagements")
- **Authentication**: Choose between:
  - Username and password
  - API key

### Authentication Options:

**Option 1: Username/Password**
```
Username: your_username
Password: your_password
```

**Option 2: API Key**
```
API key: your_base64_encoded_api_key
```

### Environment Variables (for automation):
For non-interactive use, set these environment variables:

**Username/Password:**
```bash
export ES_CLUSTER_URL="https://your-cluster.es.region.aws.elastic-cloud.com"
export ES_USERNAME="your_username"
export ES_PASSWORD="your_password"
export ES_INDEX="specialist-engagements"  # optional
```

**API Key:**
```bash
export ES_CLUSTER_URL="https://your-cluster.es.region.aws.elastic-cloud.com"
export ES_API_KEY="your_base64_encoded_api_key"
export ES_INDEX="specialist-engagements"  # optional
```

### Security Features:
- SSL certificate verification is disabled for flexibility
- Credentials are never stored in files
- API key support for enhanced security

## Usage

### 1. Interactive Mode (Recommended for beginners)

```bash
python interactive_sf_to_es.py
```

This provides a menu-driven interface that guides you through:
- Testing connections
- Processing single URLs
- Batch processing files
- Viewing configuration
- Checking index status

### 2. Single Opportunity Processing

```bash
python sf_to_elasticsearch.py "https://elastic.lightning.force.com/lightning/r/Opportunity/0064R00000XXXXXX/view"
```

### 3. Batch Processing

```bash
python batch_sf_to_elasticsearch.py opportunity_urls.txt
```

Create a text file with one opportunity URL per line:
```
https://elastic.lightning.force.com/lightning/r/Opportunity/0064R00000XXXXXX/view
https://elastic.lightning.force.com/lightning/r/Opportunity/0064R00000YYYYYY/view
https://elastic.lightning.force.com/lightning/r/Opportunity/0064R00000ZZZZZZ/view
```

## Data Fields

The tool extracts and indexes the following fields:

| Salesforce Field | Elasticsearch Field | Description |
|------------------|---------------------|-------------|
| Id | opportunity_id | Unique opportunity identifier |
| Name | opportunity_name | Opportunity name |
| Account.Name | account_name | Associated account name |
| CloseDate | close_date | Expected close date |
| Amount | amount | Opportunity amount |
| TCV__c | tcv_amount | Total Contract Value |
| - | extracted_at | Timestamp of extraction |
| - | source | Source system identifier |

## URL Formats Supported

The tool can extract opportunity IDs from these URL formats:

- Lightning Experience: `https://elastic.lightning.force.com/lightning/r/Opportunity/006XXXXXXXXXXXXX/view`
- Classic: `https://elastic.my.salesforce.com/006XXXXXXXXXXXXX`
- Direct ID: `006XXXXXXXXXXXXX` (15 or 18 character format)

## Logging

All operations are logged to:
- `sf_to_es.log` (single processing)
- `batch_sf_to_es.log` (batch processing)
- `interactive_sf_to_es.log` (interactive mode)

Log levels can be configured in `config.py`.

## Error Handling

The tool handles common scenarios:
- Invalid URLs
- Missing opportunities
- Authentication failures
- Network connectivity issues
- Elasticsearch indexing errors

## File Structure

```
├── sf_auth.py                    # Salesforce authentication module
├── sf_to_elasticsearch.py        # Single opportunity processor
├── batch_sf_to_elasticsearch.py  # Batch processor
├── interactive_sf_to_es.py       # Interactive interface
├── config.py                     # Configuration settings
├── README.md                     # This documentation
├── requirements.txt              # Python dependencies
└── examples/
    ├── sample_urls.txt           # Example URL file
    └── sample_output.json        # Example output format
```

## Elasticsearch Index Structure

The tool creates an index with this mapping:

```json
{
  "mappings": {
    "properties": {
      "opportunity_id": {"type": "keyword"},
      "opportunity_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
      "account_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
      "close_date": {"type": "date"},
      "amount": {"type": "double"},
      "tcv_amount": {"type": "double"},
      "extracted_at": {"type": "date"},
      "source": {"type": "keyword"}
    }
  }
}
```

## Troubleshooting

### Authentication Issues
1. Ensure Salesforce CLI is installed: `sf --version`
2. Check authentication: `sf org list`
3. Re-authenticate if needed: `sf org login web -r https://elastic.my.salesforce.com`

### Elasticsearch Connection
1. Verify cluster URL format: `https://your-cluster.es.region.aws.elastic-cloud.com`
2. Check authentication credentials (username/password or API key)
3. Ensure cluster is accessible from your network
4. SSL verification is disabled, so certificate issues shouldn't occur

### Configuration Issues
1. Use environment variables for automation: `ES_CLUSTER_URL`, `ES_USERNAME`, etc.
2. API keys should be base64 encoded
3. Check that your user has index creation and document indexing permissions

### URL Extraction Failures
1. Use the interactive mode's URL tester
2. Check URL format against supported patterns
3. Ensure opportunity ID starts with '006'

### Performance Optimization
1. Use batch processing for multiple opportunities
2. Monitor Elasticsearch cluster resources
3. Adjust batch sizes in `config.py` if needed

---

## ✨ **Ready to Start**

The toolkit is production-ready with comprehensive error handling, extensive documentation, and diagnostic tools for troubleshooting. Your fraud detection and AML compliance workflows will immediately benefit from the integrated case investigation capabilities and cross-reference analysis features.

**Start here:**
```bash
./setup.sh
python3 sf_closed_simple.py
```

**Then explore:**
```bash
python3 sf_account_simple.py "account_url"
python3 sf_cases_simple.py --priority High
```

**Finally, integrate:**
```bash
python3 sf_closed_opportunities.py
python3 sf_cases_to_elasticsearch.py --with-comments
```

Happy analyzing! 🎯
