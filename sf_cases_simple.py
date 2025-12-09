#!/usr/bin/env python3
"""
Simple Salesforce Cases Analysis Tool

Quick analysis of Salesforce cases with instant insights.
JSON output only - no Elasticsearch required.

Features:
- Quick case statistics
- Status, priority, and origin breakdowns
- Account-level analysis
- Recent activity trends

Usage:
    python3 sf_cases_simple.py                     # All cases
    python3 sf_cases_simple.py --account-id ID     # Specific account
    python3 sf_cases_simple.py --open-only         # Open cases only
    python3 sf_cases_simple.py --closed-only       # Closed cases only
    python3 sf_cases_simple.py --limit 100         # Limit results
"""

import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sf_auth import get_salesforce_connection

def extract_account_id(url: str) -> Optional[str]:
    """Extract Salesforce Account ID from URL."""
    import re
    patterns = [
        r'/([A-Za-z0-9]{15,18})',
        r'/Account/([A-Za-z0-9]{15,18})',
        r'001[A-Za-z0-9]{12,15}',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            account_id = match.group(1) if len(match.groups()) > 0 else match.group(0)
            if account_id.startswith('001') and len(account_id) >= 15:
                return account_id
    
    # Try as raw ID
    if url.startswith('001') and 15 <= len(url) <= 18:
        return url
        
    return None

def get_cases(sf, account_id: Optional[str] = None, open_only: bool = False, 
              closed_only: bool = False, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Retrieve cases from Salesforce."""
    
    # Build SOQL query
    soql = """
    SELECT 
        Id, CaseNumber, Subject, Status, Priority, Type, Origin,
        AccountId, Account.Name, 
        CreatedDate, ClosedDate, IsClosed, IsEscalated,
        Owner.Name, CreatedBy.Name
    FROM Case
    """
    
    # Add WHERE conditions
    where_conditions = []
    
    if account_id:
        where_conditions.append(f"AccountId = '{account_id}'")
    
    if open_only:
        where_conditions.append("IsClosed = false")
    elif closed_only:
        where_conditions.append("IsClosed = true")
    
    if where_conditions:
        soql += " WHERE " + " AND ".join(where_conditions)
    
    # Add ordering
    soql += " ORDER BY CreatedDate DESC"
    
    # Add limit
    if limit:
        soql += f" LIMIT {limit}"
    
    print(f"🔍 Querying cases...")
    result = sf.query_all(soql)
    return result['records']

def analyze_cases(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze cases and provide quick statistics."""
    
    if not cases:
        return {'total_cases': 0}
    
    analysis = {
        'total_cases': len(cases),
        'open_cases': 0,
        'closed_cases': 0,
        'escalated_cases': 0,
        'by_status': {},
        'by_priority': {},
        'by_type': {},
        'by_origin': {},
        'by_account': {},
        'recent_cases_7d': 0,
        'recent_cases_30d': 0,
        'top_cases': []
    }
    
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)
    
    for case in cases:
        # Basic counts
        if case['IsClosed']:
            analysis['closed_cases'] += 1
        else:
            analysis['open_cases'] += 1
        
        if case['IsEscalated']:
            analysis['escalated_cases'] += 1
        
        # Status breakdown
        status = case['Status']
        analysis['by_status'][status] = analysis['by_status'].get(status, 0) + 1
        
        # Priority breakdown
        priority = case['Priority'] or 'No Priority'
        analysis['by_priority'][priority] = analysis['by_priority'].get(priority, 0) + 1
        
        # Type breakdown
        case_type = case['Type'] or 'No Type'
        analysis['by_type'][case_type] = analysis['by_type'].get(case_type, 0) + 1
        
        # Origin breakdown
        origin = case['Origin'] or 'No Origin'
        analysis['by_origin'][origin] = analysis['by_origin'].get(origin, 0) + 1
        
        # Account grouping
        account_name = case['Account']['Name'] if case.get('Account') else 'No Account'
        if account_name not in analysis['by_account']:
            analysis['by_account'][account_name] = {
                'total': 0,
                'open': 0,
                'closed': 0,
                'escalated': 0
            }
        
        analysis['by_account'][account_name]['total'] += 1
        if case['IsClosed']:
            analysis['by_account'][account_name]['closed'] += 1
        else:
            analysis['by_account'][account_name]['open'] += 1
        if case['IsEscalated']:
            analysis['by_account'][account_name]['escalated'] += 1
        
        # Recent cases
        created_date = datetime.fromisoformat(case['CreatedDate'].replace('Z', '+00:00'))
        if created_date.replace(tzinfo=None) >= seven_days_ago:
            analysis['recent_cases_7d'] += 1
        if created_date.replace(tzinfo=None) >= thirty_days_ago:
            analysis['recent_cases_30d'] += 1
        
        # Top cases for display
        if len(analysis['top_cases']) < 10:
            case_info = {
                'case_number': case['CaseNumber'],
                'subject': case['Subject'],
                'status': case['Status'],
                'priority': case['Priority'],
                'account': account_name,
                'created_date': case['CreatedDate'],
                'is_closed': case['IsClosed']
            }
            analysis['top_cases'].append(case_info)
    
    return analysis

def display_analysis(analysis: Dict[str, Any]):
    """Display case analysis in a user-friendly format."""
    
    print(f"\n🎫 SALESFORCE CASES QUICK ANALYSIS")
    print("=" * 45)
    
    if analysis['total_cases'] == 0:
        print("❌ No cases found matching criteria")
        return
    
    print(f"\n📊 OVERVIEW:")
    print(f"   Total Cases: {analysis['total_cases']:,}")
    print(f"   Open: {analysis['open_cases']:,}")
    print(f"   Closed: {analysis['closed_cases']:,}")
    print(f"   Escalated: {analysis['escalated_cases']:,}")
    
    # Calculate percentages
    if analysis['total_cases'] > 0:
        open_pct = (analysis['open_cases'] / analysis['total_cases']) * 100
        closed_pct = (analysis['closed_cases'] / analysis['total_cases']) * 100
        escalated_pct = (analysis['escalated_cases'] / analysis['total_cases']) * 100
        
        print(f"   Open Rate: {open_pct:.1f}%")
        print(f"   Close Rate: {closed_pct:.1f}%")
        print(f"   Escalation Rate: {escalated_pct:.1f}%")
    
    print(f"\n📅 RECENT ACTIVITY:")
    print(f"   Last 7 days: {analysis['recent_cases_7d']:,} cases")
    print(f"   Last 30 days: {analysis['recent_cases_30d']:,} cases")
    
    # Status breakdown
    print(f"\n📋 STATUS BREAKDOWN:")
    for status, count in sorted(analysis['by_status'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / analysis['total_cases']) * 100
        print(f"   {status}: {count:,} ({percentage:.1f}%)")
    
    # Priority breakdown
    print(f"\n⚡ PRIORITY BREAKDOWN:")
    priority_order = ['High', 'Medium', 'Low', 'No Priority']
    # Sort by priority order, then by count
    sorted_priorities = sorted(
        analysis['by_priority'].items(),
        key=lambda x: (priority_order.index(x[0]) if x[0] in priority_order else 999, -x[1])
    )
    for priority, count in sorted_priorities:
        percentage = (count / analysis['total_cases']) * 100
        print(f"   {priority}: {count:,} ({percentage:.1f}%)")
    
    # Origin breakdown (top 5)
    print(f"\n📥 TOP CASE ORIGINS:")
    for origin, count in sorted(analysis['by_origin'].items(), key=lambda x: x[1], reverse=True)[:5]:
        percentage = (count / analysis['total_cases']) * 100
        print(f"   {origin}: {count:,} ({percentage:.1f}%)")
    
    # Account breakdown (top 10)
    print(f"\n🏢 TOP ACCOUNTS BY CASE VOLUME:")
    sorted_accounts = sorted(
        analysis['by_account'].items(),
        key=lambda x: x[1]['total'],
        reverse=True
    )[:10]
    
    for account_name, stats in sorted_accounts:
        print(f"   {account_name}: {stats['total']:,} cases")
        print(f"      Open: {stats['open']}, Closed: {stats['closed']}, Escalated: {stats['escalated']}")
    
    # Recent cases
    print(f"\n📋 RECENT CASES:")
    for i, case in enumerate(analysis['top_cases'][:5], 1):
        status_emoji = "🔓" if not case['is_closed'] else "🔒"
        priority_emoji = {"High": "🔥", "Medium": "⚡", "Low": "📝"}.get(case['priority'], "📋")
        
        print(f"   {i}. {status_emoji} {case['case_number']} - {case['subject'][:50]}...")
        print(f"      {priority_emoji} {case['priority'] or 'No Priority'} | {case['status']} | {case['account']}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Quick Salesforce Cases Analysis")
    
    parser.add_argument('account_urls', nargs='*', 
                       help='Account URLs to filter cases by')
    parser.add_argument('--account-id', 
                       help='Specific Account ID to filter cases by')
    parser.add_argument('--open-only', action='store_true',
                       help='Only retrieve open cases')
    parser.add_argument('--closed-only', action='store_true',
                       help='Only retrieve closed cases')
    parser.add_argument('--limit', type=int, default=1000,
                       help='Limit the number of cases retrieved (default: 1000)')
    parser.add_argument('--output-file',
                       help='Save results to JSON file')
    
    args = parser.parse_args()
    
    # Connect to Salesforce
    try:
        sf = get_salesforce_connection()
        print("✅ Connected to Salesforce")
    except Exception as e:
        print(f"❌ Failed to connect to Salesforce: {str(e)}")
        sys.exit(1)
    
    # Determine account ID filter
    account_id = args.account_id
    if args.account_urls:
        account_id = extract_account_id(args.account_urls[0])
        if not account_id:
            print(f"❌ Could not extract account ID from URL: {args.account_urls[0]}")
            sys.exit(1)
        print(f"🎯 Analyzing cases for Account: {account_id}")
    
    # Retrieve and analyze cases
    cases = get_cases(
        sf,
        account_id=account_id,
        open_only=args.open_only,
        closed_only=args.closed_only,
        limit=args.limit
    )
    
    analysis = analyze_cases(cases)
    display_analysis(analysis)
    
    # Save to file if requested
    if args.output_file:
        output_data = {
            'analysis': analysis,
            'raw_cases': cases,
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'total_cases': len(cases),
                'filters': {
                    'account_id': account_id,
                    'open_only': args.open_only,
                    'closed_only': args.closed_only,
                    'limit': args.limit
                }
            }
        }
        
        with open(args.output_file, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {args.output_file}")
    
    print(f"\n💡 TIP: Use sf_cases_to_elasticsearch.py for full ES integration and case comments")

if __name__ == "__main__":
    main()
