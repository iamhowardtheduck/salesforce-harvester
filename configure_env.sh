#!/bin/bash
# Environment Variables Configuration for Salesforce to Elasticsearch Tools
# Updated for the complete tool suite including account analysis and closed opportunities

echo "🔧 Elasticsearch Environment Variables Configuration"
echo "===================================================="

echo ""
echo "This script helps you configure environment variables for automated processing"
echo "across all Salesforce to Elasticsearch tools including:"
echo "  • Opportunity processing (single, batch, interactive)"
echo "  • Closed opportunities analysis"  
echo "  • Account-specific opportunity analysis"
echo "  • Sales dashboard and reporting"

echo ""
echo "🔐 Choose your authentication method:"
echo "1. Username and Password (basic auth)"
echo "2. API Key (recommended for security)"
read -p "Enter choice (1/2): " auth_choice

echo ""
echo "🌐 Enter your Elasticsearch cluster URL:"
echo "Examples:"
echo "  • Elastic Cloud: https://your-cluster.es.region.aws.elastic-cloud.com"
echo "  • Self-hosted: https://elasticsearch.yourcompany.com:9200"
echo "  • Local: http://localhost:9200"
read -p "Cluster URL: " cluster_url

echo ""
echo "📚 Choose your index configuration:"
echo "1. Single index for all data (recommended)"
echo "2. Separate indices by data type"
read -p "Enter choice (1/2): " index_choice

if [ "$index_choice" = "2" ]; then
    echo ""
    echo "📋 Enter index names (or press Enter for defaults):"
    read -p "Opportunities index [opportunities]: " opportunities_index
    read -p "Account opportunities index [account-opportunities]: " account_index
    read -p "Closed opportunities index [closed-opportunities]: " closed_index
    
    opportunities_index=${opportunities_index:-opportunities}
    account_index=${account_index:-account-opportunities}
    closed_index=${closed_index:-closed-opportunities}
else
    echo ""
    echo "📋 Enter your index name (or press Enter for default):"
    read -p "Index [specialist-engagements]: " index_name
    index_name=${index_name:-specialist-engagements}
    
    opportunities_index="$index_name"
    account_index="$index_name"
    closed_index="$index_name"
fi

echo ""

# Export common variables
export ES_CLUSTER_URL="$cluster_url"
export ES_INDEX="$opportunities_index"  # Default index

# Export specific indices if using separate ones
if [ "$index_choice" = "2" ]; then
    export ES_OPPORTUNITIES_INDEX="$opportunities_index"
    export ES_ACCOUNT_INDEX="$account_index"
    export ES_CLOSED_INDEX="$closed_index"
fi

if [ "$auth_choice" = "2" ]; then
    # API Key authentication
    echo "🔑 Enter your API key:"
    echo "💡 Generate in Kibana: Stack Management > API Keys"
    echo "   Copy the base64 encoded key (starts with 'encoded_key=')"
    read -s api_key
    export ES_API_KEY="$api_key"
    
    echo ""
    echo "✅ Environment variables set for API key authentication:"
    echo "export ES_CLUSTER_URL=\"$ES_CLUSTER_URL\""
    echo "export ES_INDEX=\"$ES_INDEX\""
    if [ "$index_choice" = "2" ]; then
        echo "export ES_OPPORTUNITIES_INDEX=\"$ES_OPPORTUNITIES_INDEX\""
        echo "export ES_ACCOUNT_INDEX=\"$ES_ACCOUNT_INDEX\""
        echo "export ES_CLOSED_INDEX=\"$ES_CLOSED_INDEX\""
    fi
    echo "export ES_API_KEY=\"[HIDDEN]\""
    
else
    # Username/Password authentication
    echo "👤 Enter your Elasticsearch username:"
    read -p "Username: " username
    echo "🔒 Enter your Elasticsearch password (will be hidden):"
    read -s password
    
    export ES_USERNAME="$username"
    export ES_PASSWORD="$password"
    
    echo ""
    echo "✅ Environment variables set for username/password authentication:"
    echo "export ES_CLUSTER_URL=\"$ES_CLUSTER_URL\""
    echo "export ES_USERNAME=\"$ES_USERNAME\""
    echo "export ES_PASSWORD=\"[HIDDEN]\""
    echo "export ES_INDEX=\"$ES_INDEX\""
    if [ "$index_choice" = "2" ]; then
        echo "export ES_OPPORTUNITIES_INDEX=\"$ES_OPPORTUNITIES_INDEX\""
        echo "export ES_ACCOUNT_INDEX=\"$ES_ACCOUNT_INDEX\""
        echo "export ES_CLOSED_INDEX=\"$ES_CLOSED_INDEX\""
    fi
fi

echo ""
echo "🚀 READY TO USE - Example Commands:"
echo "=================================="

echo ""
echo "📊 Opportunity Processing:"
echo "   python3 sf_to_elasticsearch.py 'opportunity_url'"
echo "   python3 batch_sf_to_elasticsearch.py opportunities.txt"
echo "   python3 interactive_sf_to_es.py"

echo ""
echo "📈 Closed Opportunities Analysis:"
echo "   python3 sf_closed_opportunities.py                    # All closed opps to ES"
echo "   python3 sf_closed_opportunities.py --won-only         # Won opportunities only"
echo "   python3 sf_closed_opportunities.py --json-only        # JSON output only"

echo ""
echo "🏢 Account-Specific Analysis:"
echo "   python3 sf_account_opportunities.py 'account_url'     # Single account to ES"
echo "   python3 sf_account_opportunities.py --accounts-file key_accounts.txt"
echo "   python3 sf_account_opportunities.py --json-only 'account_url'"

echo ""
echo "🎯 Sales Dashboard:"
echo "   python3 sf_sales_dashboard.py --one-time             # One-time snapshot"
echo "   python3 sf_sales_dashboard.py                        # Live dashboard"

echo ""
echo "🧪 Testing & Validation:"
echo "   python3 test_validation.py                           # Comprehensive tests"
echo "   python3 sf_to_json.py 'opportunity_url'              # Test without ES"

echo ""
echo "💡 To make these settings permanent, add the export commands to your shell profile:"
echo "   ~/.bashrc (Linux), ~/.zshrc (macOS), or ~/.bash_profile"

# Offer to save to a file
echo ""
read -p "💾 Save these settings to a configuration file? (y/N): " save_choice
if [[ $save_choice =~ ^[Yy]$ ]]; then
    config_file="es_config_$(date +%Y%m%d_%H%M%S).sh"
    
    echo "#!/bin/bash" > "$config_file"
    echo "# Elasticsearch configuration generated on $(date)" >> "$config_file"
    echo "# For Salesforce to Elasticsearch Integration Tool Suite" >> "$config_file"
    echo "" >> "$config_file"
    echo "# Primary configuration" >> "$config_file"
    echo "export ES_CLUSTER_URL=\"$ES_CLUSTER_URL\"" >> "$config_file"
    echo "export ES_INDEX=\"$ES_INDEX\"" >> "$config_file"
    
    if [ "$index_choice" = "2" ]; then
        echo "" >> "$config_file"
        echo "# Separate indices for different data types" >> "$config_file"
        echo "export ES_OPPORTUNITIES_INDEX=\"$ES_OPPORTUNITIES_INDEX\"" >> "$config_file"
        echo "export ES_ACCOUNT_INDEX=\"$ES_ACCOUNT_INDEX\"" >> "$config_file"
        echo "export ES_CLOSED_INDEX=\"$ES_CLOSED_INDEX\"" >> "$config_file"
    fi
    
    echo "" >> "$config_file"
    echo "# Authentication" >> "$config_file"
    if [ "$auth_choice" = "2" ]; then
        echo "export ES_API_KEY=\"$ES_API_KEY\"" >> "$config_file"
    else
        echo "export ES_USERNAME=\"$ES_USERNAME\"" >> "$config_file"
        echo "export ES_PASSWORD=\"$ES_PASSWORD\"" >> "$config_file"
    fi
    
    echo "" >> "$config_file"
    echo "# Usage examples:" >> "$config_file"
    echo "# python3 sf_closed_opportunities.py" >> "$config_file"
    echo "# python3 sf_account_opportunities.py 'account_url'" >> "$config_file"
    echo "# python3 batch_sf_to_elasticsearch.py urls.txt" >> "$config_file"
    
    chmod +x "$config_file"
    echo "✅ Configuration saved to $config_file"
    echo ""
    echo "📖 To use this configuration:"
    echo "   source $config_file                               # Load in current session"
    echo "   echo 'source $(pwd)/$config_file' >> ~/.bashrc    # Load automatically"
fi

echo ""
echo "🧪 TEST YOUR CONFIGURATION:"
echo "=========================="

echo ""
echo "1. Test basic imports:"
echo "   python3 test_validation.py"

echo ""
echo "2. Test Elasticsearch connection (if configured):"
if [ "$auth_choice" = "2" ]; then
    echo "   curl -X GET \"$ES_CLUSTER_URL/_cluster/health\" -H \"Authorization: ApiKey $ES_API_KEY\""
else
    echo "   curl -X GET \"$ES_CLUSTER_URL/_cluster/health\" -u \"$ES_USERNAME:$ES_PASSWORD\""
fi

echo ""
echo "3. Test Salesforce connection:"
echo "   python3 sf_to_json.py 'your_opportunity_url'"

echo ""
echo "4. Test full pipeline:"
echo "   python3 sf_to_elasticsearch.py 'your_opportunity_url'"

echo ""
echo "🎉 Configuration complete! Your tools are ready for production use."
echo ""
echo "📚 Need help? Check the documentation:"
echo "   • README.md - Complete guide"
echo "   • ELASTICSEARCH_ACCOUNT_CONFIG.md - ES configuration details"
echo "   • *_GUIDE.md files - Tool-specific guides"
