#!/bin/bash

# setup.sh - Complete Setup for Salesforce to Elasticsearch Integration
#
# This script sets up the complete environment including:
# - Python dependencies installation
# - Environment configuration validation
# - Elasticsearch ingest pipeline installation
# - Index template installation  
# - Connection testing and validation
# - Directory structure creation
#
# Usage:
#   ./setup.sh                # Complete setup
#   ./setup.sh --skip-deps    # Skip Python dependency installation
#   ./setup.sh --config-only  # Only test configuration
#   ./setup.sh --templates-only # Only install ES templates and pipelines

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_success() {
    print_status "$GREEN" "✅ $1"
}

print_error() {
    print_status "$RED" "❌ $1"
}

print_warning() {
    print_status "$YELLOW" "⚠️  $1"
}

print_info() {
    print_status "$BLUE" "ℹ️  $1"
}

print_header() {
    print_status "$PURPLE" "🔧 $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        local version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        local major=$(echo $version | cut -d. -f1)
        local minor=$(echo $version | cut -d. -f2)
        
        if [ "$major" -eq 3 ] && [ "$minor" -ge 7 ]; then
            print_success "Python $version detected"
            return 0
        else
            print_error "Python 3.7+ required (found: $version)"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

# Function to install Python dependencies
install_dependencies() {
    if [ "$SKIP_DEPS" = "true" ]; then
        print_info "Skipping dependency installation"
        return 0
    fi

    print_header "INSTALLING PYTHON DEPENDENCIES"
    echo
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        return 1
    fi
    
    print_info "Installing Python packages from requirements.txt..."
    
    # Try pip3 first, then pip
    if command_exists pip3; then
        pip3 install --user -r requirements.txt
    elif command_exists pip; then
        pip install --user -r requirements.txt
    else
        print_error "pip not found. Please install pip first."
        return 1
    fi
    
    print_success "Python dependencies installed"
    echo
}

# Function to check and load environment configuration
load_environment() {
    print_header "LOADING ENVIRONMENT CONFIGURATION"
    echo
    
    # Check for .env file
    if [ -f ".env" ]; then
        print_info "Loading configuration from .env file..."
        set -a  # automatically export all variables
        source .env
        set +a
        print_success "Environment loaded from .env"
    else
        print_warning ".env file not found"
        print_info "Run 'python3 configure.py' to create configuration"
        
        # Try to use environment variables directly
        if [ -z "$ES_CLUSTER_URL" ]; then
            print_error "ES_CLUSTER_URL not set"
            print_info "Please run: python3 configure.py"
            return 1
        fi
    fi
    
    # Validate required environment variables
    local required_vars=("ES_CLUSTER_URL")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing required environment variables: ${missing_vars[*]}"
        return 1
    fi
    
    # Check authentication
    if [ -n "$ES_API_KEY" ]; then
        AUTH_TYPE="api_key"
        print_success "API Key authentication configured"
    elif [ -n "$ES_USERNAME" ] && [ -n "$ES_PASSWORD" ]; then
        AUTH_TYPE="basic"
        print_success "Basic authentication configured"
    else
        print_error "No Elasticsearch authentication configured"
        print_info "Set either ES_API_KEY or ES_USERNAME+ES_PASSWORD"
        return 1
    fi
    
    # Set default index if not specified
    if [ -z "$ES_INDEX" ]; then
        export ES_INDEX="salesforce-opps"
        print_info "Using default index: $ES_INDEX"
    else
        print_success "Target index: $ES_INDEX"
    fi
    
    echo
}

# Function to test Elasticsearch connection
test_elasticsearch_connection() {
    print_header "TESTING ELASTICSEARCH CONNECTION"
    echo
    
    # Build curl command based on authentication type
    local curl_cmd="curl -s -k --max-time 10"
    
    if [ "$AUTH_TYPE" = "api_key" ]; then
        curl_cmd="$curl_cmd -H 'Authorization: ApiKey $ES_API_KEY'"
    elif [ "$AUTH_TYPE" = "basic" ]; then
        curl_cmd="$curl_cmd -u '$ES_USERNAME:$ES_PASSWORD'"
    fi
    
    print_info "Testing connection to: $ES_CLUSTER_URL"
    
    # Test basic connectivity
    local response=$(eval "$curl_cmd '$ES_CLUSTER_URL'")
    local exit_code=$?
    
    if [ $exit_code -eq 0 ] && echo "$response" | grep -q '"cluster_name"'; then
        local cluster_name=$(echo "$response" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('cluster_name', 'Unknown'))" 2>/dev/null)
        local version=$(echo "$response" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('version', {}).get('number', 'Unknown'))" 2>/dev/null)
        
        print_success "Connection successful"
        print_info "Cluster: $cluster_name"
        print_info "Version: $version"
        echo
        return 0
    else
        print_error "Connection failed"
        if [ $exit_code -eq 28 ]; then
            print_error "Connection timeout - check URL and network"
        elif [ $exit_code -eq 22 ]; then
            print_error "HTTP error - check authentication credentials"
        else
            print_error "Network error (exit code: $exit_code)"
        fi
        
        echo
        print_info "Troubleshooting tips:"
        echo "  • Verify ES_CLUSTER_URL is correct"
        echo "  • Check network connectivity"
        echo "  • Validate authentication credentials"
        echo "  • Ensure Elasticsearch is running"
        echo
        return 1
    fi
}

# Function to install ingest pipeline
install_ingest_pipeline() {
    print_header "INSTALLING INGEST PIPELINE"
    echo
    
    local pipeline_file="sf-to-es.json"
    
    if [ ! -f "$pipeline_file" ]; then
        print_error "Pipeline file not found: $pipeline_file"
        return 1
    fi
    
    print_info "Installing ingest pipeline: sf-to-es"
    
    # Build curl command for pipeline installation
    local curl_cmd="curl -s -k --max-time 30 -X PUT"
    
    if [ "$AUTH_TYPE" = "api_key" ]; then
        curl_cmd="$curl_cmd -H 'Authorization: ApiKey $ES_API_KEY'"
    elif [ "$AUTH_TYPE" = "basic" ]; then
        curl_cmd="$curl_cmd -u '$ES_USERNAME:$ES_PASSWORD'"
    fi
    
    curl_cmd="$curl_cmd -H 'Content-Type: application/json'"
    
    # Install pipeline
    local response=$(eval "$curl_cmd '$ES_CLUSTER_URL/_ingest/pipeline/sf-to-es' -d @'$pipeline_file'")
    local exit_code=$?
    
    if [ $exit_code -eq 0 ] && echo "$response" | grep -q '"acknowledged".*true'; then
        print_success "Ingest pipeline installed: sf-to-es"
        
        # Verify pipeline installation
        local verify_response=$(eval "curl -s -k -H 'Authorization: ApiKey $ES_API_KEY' '$ES_CLUSTER_URL/_ingest/pipeline/sf-to-es'")
        if echo "$verify_response" | grep -q '"sf-to-es"'; then
            local processor_count=$(echo "$verify_response" | python3 -c "import json,sys; data=json.load(sys.stdin); print(len(data.get('sf-to-es', {}).get('processors', [])))" 2>/dev/null)
            print_info "Pipeline processors: $processor_count"
        fi
        
    else
        print_error "Failed to install ingest pipeline"
        if [ $exit_code -ne 0 ]; then
            print_error "Network error (exit code: $exit_code)"
        else
            print_error "Response: $response"
        fi
        return 1
    fi
    
    echo
}

# Function to install index template
install_index_template() {
    print_header "INSTALLING INDEX TEMPLATE"
    echo
    
    local template_file="salesforce-to-es-template.json"
    
    if [ ! -f "$template_file" ]; then
        print_error "Template file not found: $template_file"
        return 1
    fi
    
    # Update template for custom index if needed
    local template_content=""
    if [ "$ES_INDEX" != "salesforce-opps" ]; then
        print_info "Updating template for custom index: $ES_INDEX"
        template_content=$(python3 -c "
import json
import sys

# Read template file
with open('$template_file', 'r') as f:
    template = json.load(f)

# Update index patterns for custom index
template['index_patterns'] = ['${ES_INDEX}*']

# Output updated template
print(json.dumps(template, indent=2))
")
    else
        template_content=$(cat "$template_file")
    fi
    
    print_info "Installing index template: salesforce-to-es-template"
    
    # Build curl command for template installation
    local curl_cmd="curl -s -k --max-time 30 -X PUT"
    
    if [ "$AUTH_TYPE" = "api_key" ]; then
        curl_cmd="$curl_cmd -H 'Authorization: ApiKey $ES_API_KEY'"
    elif [ "$AUTH_TYPE" = "basic" ]; then
        curl_cmd="$curl_cmd -u '$ES_USERNAME:$ES_PASSWORD'"
    fi
    
    curl_cmd="$curl_cmd -H 'Content-Type: application/json'"
    
    # Install template
    local response=$(echo "$template_content" | eval "$curl_cmd '$ES_CLUSTER_URL/_index_template/salesforce-to-es-template' -d @-")
    local exit_code=$?
    
    if [ $exit_code -eq 0 ] && echo "$response" | grep -q '"acknowledged".*true'; then
        print_success "Index template installed: salesforce-to-es-template"
        
        if [ "$ES_INDEX" != "salesforce-opps" ]; then
            print_info "Template configured for index pattern: ${ES_INDEX}*"
        else
            print_info "Template configured for index pattern: salesforce-opps*"
        fi
        
    else
        print_error "Failed to install index template"
        if [ $exit_code -ne 0 ]; then
            print_error "Network error (exit code: $exit_code)"
        else
            print_error "Response: $response"
        fi
        return 1
    fi
    
    echo
}

# Function to create necessary directories
create_directories() {
    print_header "CREATING DIRECTORIES"
    echo
    
    local dirs=("logs" "opportunity_exports")
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        else
            print_info "Directory exists: $dir"
        fi
    done
    
    echo
}

# Function to validate file permissions
check_permissions() {
    print_header "CHECKING FILE PERMISSIONS"
    echo
    
    local scripts=("sf_to_es.py" "sf_auth.py" "configure.py" "interactive_sf_to_es.py" "es_diagnostics.py")
    
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            if [ -r "$script" ]; then
                print_success "Readable: $script"
            else
                print_error "Not readable: $script"
                chmod +r "$script" 2>/dev/null && print_success "Fixed permissions: $script"
            fi
        else
            print_warning "Missing script: $script"
        fi
    done
    
    # Check if main scripts are executable
    local executable_scripts=("sf_to_es.py" "configure.py" "interactive_sf_to_es.py")
    
    for script in "${executable_scripts[@]}"; do
        if [ -f "$script" ] && [ ! -x "$script" ]; then
            chmod +x "$script" 2>/dev/null && print_info "Made executable: $script"
        fi
    done
    
    echo
}

# Function to run comprehensive tests
run_tests() {
    print_header "RUNNING INTEGRATION TESTS"
    echo
    
    # Test Python imports
    print_info "Testing Python dependencies..."
    if python3 -c "import simple_salesforce, elasticsearch; print('✅ Core dependencies available')" 2>/dev/null; then
        print_success "Python dependencies OK"
    else
        print_error "Python dependency test failed"
        return 1
    fi
    
    # Test Salesforce CLI
    print_info "Testing Salesforce CLI..."
    if command_exists sf; then
        print_success "Salesforce CLI available"
    else
        print_warning "Salesforce CLI not found"
        print_info "Install from: https://developer.salesforce.com/tools/sfdxcli"
    fi
    
    # Run Elasticsearch diagnostics
    if [ -f "es_diagnostics.py" ]; then
        print_info "Running Elasticsearch diagnostics..."
        if python3 es_diagnostics.py >/dev/null 2>&1; then
            print_success "Elasticsearch diagnostics passed"
        else
            print_warning "Elasticsearch diagnostics issues detected"
            print_info "Run 'python3 es_diagnostics.py --full' for details"
        fi
    fi
    
    echo
}

# Function to display setup summary
display_summary() {
    print_header "SETUP COMPLETED SUCCESSFULLY!"
    echo
    echo "🎉 Your Salesforce to Elasticsearch integration is ready!"
    echo
    print_info "What was installed:"
    echo "  ✅ Python dependencies"
    echo "  ✅ Ingest pipeline: sf-to-es"
    echo "  ✅ Index template: salesforce-to-es-template"
    echo "  ✅ Directory structure"
    echo
    print_info "Configuration:"
    echo "  📊 Target index: $ES_INDEX"
    echo "  🔗 Elasticsearch: $ES_CLUSTER_URL"
    echo "  🔐 Authentication: $AUTH_TYPE"
    if [ -n "$SF_TARGET_CURRENCY" ]; then
        echo "  💱 Currency: $SF_TARGET_CURRENCY"
    fi
    echo
    print_info "Ready to use:"
    echo
    echo "  🚀 Process single opportunity:"
    echo "     python3 sf_to_es.py '<opportunity_url>'"
    echo
    echo "  📄 Process multiple opportunities:"
    echo "     python3 sf_to_es.py --file opportunity_urls.txt"
    echo
    echo "  🧪 Interactive mode:"
    echo "     python3 interactive_sf_to_es.py"
    echo
    echo "  🔍 Test connection:"
    echo "     python3 es_diagnostics.py"
    echo
    print_info "Next steps:"
    echo "  1. Authenticate with Salesforce: sf org login web"
    echo "  2. Test with a single opportunity URL"
    echo "  3. Create a file with multiple URLs for batch processing"
    echo
}

# Function to display usage help
show_help() {
    echo "Salesforce to Elasticsearch Integration Setup"
    echo
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  --skip-deps       Skip Python dependency installation"
    echo "  --config-only     Only test configuration (skip installation)"
    echo "  --templates-only  Only install Elasticsearch templates and pipelines"
    echo "  --help           Show this help message"
    echo
    echo "Examples:"
    echo "  $0                # Complete setup"
    echo "  $0 --skip-deps    # Skip dependency installation"
    echo "  $0 --config-only  # Test configuration only"
    echo
}

# Main setup function
main() {
    # Parse command line arguments
    SKIP_DEPS=false
    CONFIG_ONLY=false
    TEMPLATES_ONLY=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --config-only)
                CONFIG_ONLY=true
                shift
                ;;
            --templates-only)
                TEMPLATES_ONLY=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    echo
    print_status "$PURPLE" "🚀 ================================================= 🚀"
    print_status "$PURPLE" "   SALESFORCE TO ELASTICSEARCH INTEGRATION SETUP"
    print_status "$PURPLE" "🚀 ================================================= 🚀"
    echo
    
    # Check prerequisites
    if ! check_python_version; then
        exit 1
    fi
    
    # Load environment configuration
    if ! load_environment; then
        print_error "Environment configuration failed"
        print_info "Run 'python3 configure.py' to set up configuration"
        exit 1
    fi
    
    # Test Elasticsearch connection
    if ! test_elasticsearch_connection; then
        print_error "Elasticsearch connection failed"
        exit 1
    fi
    
    # Configuration-only mode
    if [ "$CONFIG_ONLY" = "true" ]; then
        print_success "Configuration validation completed!"
        exit 0
    fi
    
    # Install dependencies (unless skipped or templates-only)
    if [ "$TEMPLATES_ONLY" = "false" ]; then
        if ! install_dependencies; then
            print_error "Dependency installation failed"
            exit 1
        fi
    fi
    
    # Install Elasticsearch components
    if ! install_ingest_pipeline; then
        print_error "Ingest pipeline installation failed"
        exit 1
    fi
    
    if ! install_index_template; then
        print_error "Index template installation failed"
        exit 1
    fi
    
    # Create directories and check permissions (unless templates-only)
    if [ "$TEMPLATES_ONLY" = "false" ]; then
        create_directories
        check_permissions
        
        # Run tests
        if ! run_tests; then
            print_warning "Some tests failed, but setup may still be functional"
        fi
    fi
    
    # Display summary
    display_summary
}

# Run main function with all arguments
main "$@"
