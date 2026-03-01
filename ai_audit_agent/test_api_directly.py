#!/usr/bin/env python3
"""
Direct API test to diagnose the issue
Run this on the same machine where API is running
"""

import requests
import json

# Your exact data from Google Sheets
data = {
    "company_name": "ABP",
    "recipient_name": "Srujan",
    "recipient_email": "katukams@vcu.edu",
    "industry": "Food & Bevarage",
    "company_size": "Small (11-50 emplyees)",
    "annual_revenue_inr": "Less than 10 lakhs",
    "departments": {
        "Leadership & Management": {
            "track_business_metrics": "Excel spreadsheets",
            "competitor_analysis_frequency": "Monthly"
        },
        "Customer Engagement": {
            "inquiry_handling": "Basic analysis",
            "avg_response_time": "4-12 hours"
        },
        "Human Resources": {
            "recruitment_screening": "Basic filtering",
            "attendance_tracking": "Biometric/manual entry"
        },
        "Sales & Marketing": {
            "lead_management": "Manual/notebook",
            "sales_forecasting": "Manual estimates",
            "proposal_generation": "Semi-automated"
        },
        "Operations": {
            "repetitive_tasks": "Fully automated",
            "process_documentation": "Basic documentation"
        },
        "Inventory & Supply Chain": {
            "inventory_tracking": "Basic software",
            "vendor_communication": "Email chains"
        },
        "Quality Control": {
            "quality_checks": "Manual inspection",
            "defect_tracking": "Basic tracking"
        },
        "Finance & Accounting": {
            "invoice_management": "Semi-automated",
            "expense_tracking": "Smart automated"
        },
        "IT & Technology": {
            "website": "Basic static website",
            "backup_security": "Scheduled backup"
        }
    }
}

print("="*70)
print("Testing API with your exact Google Sheets data")
print("="*70)

# Test 1: Health check
print("\n1. Testing health endpoint...")
try:
    response = requests.get("http://10.246.184.25:8000/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("\n   API is not running or not reachable!")
    print("   Start it with: python main.py")
    exit(1)

# Test 2: POST to webhook
print("\n2. Testing webhook endpoint...")
try:
    response = requests.post(
        "http://10.246.184.25:8000/webhook/sheet-row",
        json=data,
        timeout=10
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    
    if response.status_code == 200:
        print("\n   ✅ SUCCESS! Webhook accepted the data")
        result = response.json()
        print(f"   Request ID: {result.get('request_id')}")
        print("\n   📧 Check email in ~60 seconds!")
    elif response.status_code == 422:
        print("\n   ❌ VALIDATION ERROR (422)")
        print("   The API rejected the data:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\n   ❌ ERROR {response.status_code}")
        print(f"   {response.text}")
        
except requests.exceptions.ConnectionError:
    print("   ❌ Cannot connect to API")
    print("\n   Make sure API is running:")
    print("   python main.py")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*70)
