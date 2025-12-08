#!/bin/bash
# Setup script for Salesforce to Elasticsearch Integration Tool

echo "🚀 Setting up Salesforce to Elasticsearch Integration Tool"
echo "=================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if SF CLI is installed
if ! command -v sf &> /dev/null; then
    echo "❌ Salesforce CLI (sf) is not installed."
    echo "📥 Install it using: brew install sf (macOS) or download from https://developer.salesforce.com/tools/sfdxcli"
    echo "⚠️  The tool will still work, but you'll need to authenticate manually."
else
    echo "✅ Salesforce CLI found: $(sf --version)"
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
if pip install -r requirements.txt --break-system-packages; then
    echo "✅ Dependencies installed successfully"
else
    echo "⚠️  Some dependencies may have failed to install"
    echo "Try: pip3 install simple-salesforce elasticsearch requests --break-system-packages"
fi

# Make scripts executable
chmod +x *.py

# Test connections (optional)
echo ""
echo "🔍 Would you like to test the connections now? (y/N)"
read -r test_connections

if [[ $test_connections =~ ^[Yy]$ ]]; then
    echo "🧪 Testing connections..."
    python3 interactive_sf_to_es.py
else
    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "📖 Next steps:"
    echo "   1. Authenticate with Salesforce: sf org login web -r https://elastic.my.salesforce.com"
    echo "   2. Run the interactive tool: python3 interactive_sf_to_es.py"
    echo "   3. You'll be prompted for your Elasticsearch cluster URL and credentials"
    echo ""
    echo "📚 Available scripts:"
    echo "   • interactive_sf_to_es.py        - Interactive menu-driven interface"
    echo "   • sf_to_elasticsearch.py        - Process single opportunity URL"
    echo "   • batch_sf_to_elasticsearch.py  - Batch process multiple URLs"
    echo ""
    echo "🔐 Authentication options:"
    echo "   • Username/password or API key for Elasticsearch"
    echo "   • Set ES_CLUSTER_URL, ES_USERNAME, ES_PASSWORD env vars for automation"
    echo "   • SSL verification is disabled for flexibility"
    echo ""
    echo "📄 See README.md for detailed documentation"
fi
