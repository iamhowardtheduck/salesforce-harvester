#!/bin/bash
# Environment Variables Configuration Example
# This script shows how to set up environment variables for automated processing

echo "🔧 Elasticsearch Environment Variables Configuration"
echo "=================================================="

echo ""
echo "Choose your authentication method:"
echo "1. Username and Password"
echo "2. API Key"
read -p "Enter choice (1/2): " auth_choice

echo ""
echo "Enter your Elasticsearch cluster URL:"
echo "Example: https://your-cluster.es.region.aws.elastic-cloud.com"
read -p "Cluster URL: " cluster_url

echo ""
echo "Enter your index name (or press Enter for default):"
read -p "Index [specialist-engagements]: " index_name
if [ -z "$index_name" ]; then
    index_name="specialist-engagements"
fi

echo ""

# Export common variables
export ES_CLUSTER_URL="$cluster_url"
export ES_INDEX="$index_name"

if [ "$auth_choice" = "2" ]; then
    # API Key authentication
    echo "Enter your API key (will be hidden):"
    read -s api_key
    export ES_API_KEY="$api_key"
    
    echo ""
    echo "✅ Environment variables set for API key authentication:"
    echo "export ES_CLUSTER_URL=\"$ES_CLUSTER_URL\""
    echo "export ES_INDEX=\"$ES_INDEX\""
    echo "export ES_API_KEY=\"[HIDDEN]\""
    
else
    # Username/Password authentication
    echo "Enter your Elasticsearch username:"
    read -p "Username: " username
    echo "Enter your Elasticsearch password (will be hidden):"
    read -s password
    
    export ES_USERNAME="$username"
    export ES_PASSWORD="$password"
    
    echo ""
    echo "✅ Environment variables set for username/password authentication:"
    echo "export ES_CLUSTER_URL=\"$ES_CLUSTER_URL\""
    echo "export ES_USERNAME=\"$ES_USERNAME\""
    echo "export ES_PASSWORD=\"[HIDDEN]\""
    echo "export ES_INDEX=\"$ES_INDEX\""
fi

echo ""
echo "🚀 You can now run the batch processor without interactive prompts:"
echo "   python3 batch_sf_to_elasticsearch.py opportunity_urls.txt"
echo ""
echo "💡 To make these permanent, add the export commands to your ~/.bashrc or ~/.zshrc"
echo ""

# Offer to save to a file
read -p "Save these settings to a file for later use? (y/N): " save_choice
if [[ $save_choice =~ ^[Yy]$ ]]; then
    config_file="es_config_$(date +%Y%m%d_%H%M%S).sh"
    
    echo "#!/bin/bash" > "$config_file"
    echo "# Elasticsearch configuration generated on $(date)" >> "$config_file"
    echo "export ES_CLUSTER_URL=\"$ES_CLUSTER_URL\"" >> "$config_file"
    echo "export ES_INDEX=\"$ES_INDEX\"" >> "$config_file"
    
    if [ "$auth_choice" = "2" ]; then
        echo "export ES_API_KEY=\"$ES_API_KEY\"" >> "$config_file"
    else
        echo "export ES_USERNAME=\"$ES_USERNAME\"" >> "$config_file"
        echo "export ES_PASSWORD=\"$ES_PASSWORD\"" >> "$config_file"
    fi
    
    chmod +x "$config_file"
    echo "✅ Configuration saved to $config_file"
    echo "   Source it with: source $config_file"
fi

echo ""
echo "🧪 Test the configuration:"
echo "   python3 test_validation.py"
