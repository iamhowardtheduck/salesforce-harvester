#!/usr/bin/env python3
"""
Tool Usage Checker

This script helps identify which tool you're using and whether it's configured 
to actually send data to Elasticsearch (not just JSON output).

Usage:
    python3 tool_checker.py
"""

import sys
import os
import subprocess
from datetime import datetime

def check_environment():
    """Check current environment setup."""
    
    print("🌍 ENVIRONMENT CHECK")
    print("=" * 25)
    
    # Check environment variables
    es_vars = [
        'ES_CLUSTER_URL', 'ES_USERNAME', 'ES_PASSWORD', 
        'ES_API_KEY', 'ES_INDEX'
    ]
    
    env_set = {}
    for var in es_vars:
        value = os.environ.get(var)
        env_set[var] = value is not None
        if value:
            if var in ['ES_PASSWORD', 'ES_API_KEY']:
                print(f"✅ {var}: [SET]")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
    
    return env_set

def analyze_command_usage():
    """Analyze which tools support ES and their usage."""
    
    print(f"\n🛠️  TOOL ELASTICSEARCH SUPPORT")
    print("=" * 35)
    
    tools = {
        'sf_to_elasticsearch.py': {
            'es_support': True,
            'json_flag': False,
            'description': 'Single URL → Elasticsearch',
            'usage': 'python3 sf_to_elasticsearch.py "opportunity_url"'
        },
        'batch_sf_to_elasticsearch.py': {
            'es_support': True,
            'json_flag': False,
            'description': 'Batch URLs → Elasticsearch',
            'usage': 'python3 batch_sf_to_elasticsearch.py urls.txt'
        },
        'interactive_sf_to_es.py': {
            'es_support': True,
            'json_flag': False,
            'description': 'Interactive interface → Elasticsearch',
            'usage': 'python3 interactive_sf_to_es.py'
        },
        'sf_closed_opportunities.py': {
            'es_support': True,
            'json_flag': True,
            'description': 'Closed opportunities analysis → ES or JSON',
            'usage': 'python3 sf_closed_opportunities.py (ES) or --json-only (JSON)'
        },
        'sf_account_opportunities.py': {
            'es_support': True,
            'json_flag': True,
            'description': 'Account opportunities → ES or JSON',
            'usage': 'python3 sf_account_opportunities.py "account_url" (ES) or --json-only (JSON)'
        },
        'sf_to_json.py': {
            'es_support': False,
            'json_flag': False,
            'description': 'Single URL → JSON only (no ES)',
            'usage': 'python3 sf_to_json.py "opportunity_url"'
        },
        'sf_explore_json.py': {
            'es_support': False,
            'json_flag': False,
            'description': 'Field exploration → JSON only',
            'usage': 'python3 sf_explore_json.py "opportunity_url"'
        },
        'sf_closed_simple.py': {
            'es_support': False,
            'json_flag': False,
            'description': 'Quick closed analysis → JSON only',
            'usage': 'python3 sf_closed_simple.py'
        },
        'sf_account_simple.py': {
            'es_support': False,
            'json_flag': False,
            'description': 'Quick account analysis → JSON only',
            'usage': 'python3 sf_account_simple.py "account_url"'
        },
        'sf_sales_dashboard.py': {
            'es_support': False,
            'json_flag': False,
            'description': 'Sales dashboard → Display only',
            'usage': 'python3 sf_sales_dashboard.py'
        }
    }
    
    print("🔥 ELASTICSEARCH INTEGRATION TOOLS:")
    for tool, info in tools.items():
        if info['es_support']:
            flag_info = " (has --json-only flag)" if info['json_flag'] else ""
            print(f"   ✅ {tool}{flag_info}")
            print(f"      {info['description']}")
    
    print(f"\n📋 JSON-ONLY TOOLS (no ES):")
    for tool, info in tools.items():
        if not info['es_support']:
            print(f"   📄 {tool}")
            print(f"      {info['description']}")
    
    return tools

def check_recent_commands():
    """Try to identify which commands were run recently."""
    
    print(f"\n📜 CHECKING FOR RECENT TOOL USAGE")
    print("=" * 40)
    
    # Check bash history for Python commands
    try:
        # Try to get recent python commands from history
        result = subprocess.run(['bash', '-c', 'history | grep python | tail -10'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout:
            print("Recent Python commands from history:")
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'sf_' in line or 'python' in line:
                    print(f"   {line.strip()}")
        else:
            print("📝 No recent Python commands found in history")
            
    except Exception:
        print("📝 Could not access command history")
    
    # Check for log files that might indicate which tool was used
    log_files = [
        'sf_to_es.log',
        'batch_sf_to_es.log', 
        'interactive_sf_to_es.log',
        'debug_batch_sf_to_es.log'
    ]
    
    print(f"\n📄 CHECKING LOG FILES:")
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                # Get last modified time
                mtime = os.path.getmtime(log_file)
                last_modified = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                
                # Get file size
                size = os.path.getsize(log_file)
                
                print(f"   📊 {log_file}: {size} bytes, modified {last_modified}")
                
                # Try to get last few lines
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"      Last entry: {lines[-1].strip()}")
                        
            except Exception as e:
                print(f"   ⚠️  {log_file}: Error reading ({e})")
        else:
            print(f"   ❌ {log_file}: Not found")

def provide_guidance():
    """Provide specific guidance based on findings."""
    
    print(f"\n🎯 TROUBLESHOOTING GUIDANCE")
    print("=" * 35)
    
    print("Most common issues:")
    print()
    
    print("1. 🚫 USING JSON-ONLY TOOLS")
    print("   Problem: Tools like sf_to_json.py, sf_closed_simple.py don't use ES")
    print("   Solution: Use sf_account_opportunities.py, sf_closed_opportunities.py")
    print()
    
    print("2. 🚫 USING --json-only FLAG")
    print("   Problem: Running with --json-only skips Elasticsearch")
    print("   Solution: Remove --json-only flag")
    print("   Example: python3 sf_closed_opportunities.py (not --json-only)")
    print()
    
    print("3. 🚫 ES CONNECTION FAILING SILENTLY")
    print("   Problem: Tool falls back to JSON when ES fails")
    print("   Solution: Run es_diagnostics.py to test connection")
    print()
    
    print("4. 🚫 WRONG INDEX NAME")
    print("   Problem: Data going to different index than expected")
    print("   Solution: Check ES_INDEX environment variable")
    print()
    
    print("5. 🚫 AUTHENTICATION ISSUES")
    print("   Problem: ES credentials wrong or expired")
    print("   Solution: Verify credentials with curl test")
    print()

def interactive_troubleshooting():
    """Interactive troubleshooting session."""
    
    print(f"\n🔍 INTERACTIVE TROUBLESHOOTING")
    print("=" * 40)
    
    print("Let's figure out what's happening...")
    print()
    
    # Ask about which tool they're using
    print("Which tool are you running? (type the number)")
    print("1. sf_closed_opportunities.py")
    print("2. sf_account_opportunities.py")
    print("3. sf_to_elasticsearch.py")
    print("4. batch_sf_to_elasticsearch.py")
    print("5. interactive_sf_to_es.py")
    print("6. Other/Not sure")
    
    try:
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            print(f"\n📊 sf_closed_opportunities.py")
            print("❓ Are you using the --json-only flag?")
            json_only = input("   (y/N): ").strip().lower()
            if json_only.startswith('y'):
                print("❌ That's the problem! Remove --json-only to use Elasticsearch")
                print("✅ Try: python3 sf_closed_opportunities.py")
            else:
                print("✅ Good, should use ES. Check connection with es_diagnostics.py")
                
        elif choice == "2":
            print(f"\n🏢 sf_account_opportunities.py")
            print("❓ Are you using the --json-only flag?")
            json_only = input("   (y/N): ").strip().lower()
            if json_only.startswith('y'):
                print("❌ That's the problem! Remove --json-only to use Elasticsearch")
                print("✅ Try: python3 sf_account_opportunities.py 'account_url'")
            else:
                print("✅ Good, should use ES. Check connection with es_diagnostics.py")
                
        elif choice in ["3", "4", "5"]:
            print(f"\n✅ Those tools always use Elasticsearch")
            print("Check connection with: python3 es_diagnostics.py")
            
        elif choice == "6":
            print(f"\n🤔 Let's identify the tool...")
            print("Are you seeing any JSON output in the terminal?")
            json_output = input("   (y/N): ").strip().lower()
            if json_output.startswith('y'):
                print("💡 You might be using a JSON-only tool or --json-only flag")
                print("🔍 Run: python3 tool_checker.py to see tool differences")
        
        print(f"\n🎯 RECOMMENDED NEXT STEPS:")
        print("1. Run: python3 es_diagnostics.py")
        print("2. Try: python3 sf_account_opportunities.py 'account_url' --verbose")
        print("3. Check Elasticsearch cluster for new data")
        
    except KeyboardInterrupt:
        print(f"\n👋 Troubleshooting cancelled")

def main():
    """Main function."""
    
    print("🔧 TOOL USAGE CHECKER")
    print("=" * 25)
    print("Checking which tools you're using and their ES configuration...")
    print()
    
    # Check environment
    env_set = check_environment()
    
    # Analyze tools
    tools = analyze_command_usage()
    
    # Check recent usage
    check_recent_commands()
    
    # Provide guidance
    provide_guidance()
    
    # Interactive troubleshooting
    print()
    run_interactive = input("🔍 Run interactive troubleshooting? (y/N): ").strip().lower()
    if run_interactive.startswith('y'):
        interactive_troubleshooting()
    else:
        print(f"\n💡 TIP: Run 'python3 es_diagnostics.py' to test your ES connection")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n👋 Tool checker cancelled")
