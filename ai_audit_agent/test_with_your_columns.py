#!/usr/bin/env python3
"""
Test script using YOUR actual Google Sheet column structure
This matches your exact columns and department categories
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def test_with_your_structure():
    """Test webhook with YOUR exact Google Sheet structure"""
    print_info("Testing with your actual column structure...")
    
    # This matches EXACTLY what your Google Sheet will send
    payload = {
        "company_name": "TechVenture Solutions Pvt Ltd",
        "recipient_name": "Rajesh Kumar",
        "recipient_email": "rajesh@techventure.com",  # Change to your email for testing
        "industry": "Information Technology Services",
        "company_size": "Medium (51-200 employees)",
        "annual_revenue_inr": "180 Cr",
        "departments": {
            # Leadership & Management
            "Leadership & Management": {
                "track_business_metrics": "Excel spreadsheets updated monthly with dashboard",
                "competitor_analysis_frequency": "Quarterly review meetings with management team"
            },
            
            # Customer Engagement
            "Customer Engagement": {
                "inquiry_handling": "Email and phone calls handled manually by customer service team",
                "avg_response_time": "12-24 hours on business days"
            },
            
            # Human Resources
            "Human Resources": {
                "recruitment_screening": "Manual CV screening followed by basic interview rounds",
                "attendance_tracking": "Biometric attendance system with Excel-based monthly reports"
            },
            
            # Sales & Marketing
            "Sales & Marketing": {
                "lead_management": "CRM software (Zoho) with manual follow-ups by sales team",
                "sales_forecasting": "Based on historical trends, no predictive analytics or AI",
                "proposal_generation": "Microsoft Word templates that are manually customized for each client"
            },
            
            # Operations
            "Operations": {
                "repetitive_tasks": "Manual execution with some Excel macros for data processing",
                "process_documentation": "Word documents and PDFs stored in shared Google Drive"
            },
            
            # Inventory & Supply Chain
            "Inventory & Supply Chain": {
                "inventory_tracking": "Excel-based tracking system with weekly manual updates",
                "vendor_communication": "Email correspondence and phone calls for orders"
            },
            
            # Quality Control
            "Quality Control": {
                "quality_checks": "Manual inspection by QC team using physical checklists",
                "defect_tracking": "Excel sheets with basic defect logging and analysis"
            },
            
            # Finance & Accounting
            "Finance & Accounting": {
                "invoice_management": "Tally ERP system with manual data entry",
                "expense_tracking": "Excel-based expense tracking with email-based approval workflow"
            },
            
            # IT & Technology
            "IT & Technology": {
                "website": "Yes, responsive dynamic website with basic analytics",
                "backup_security": "Weekly automated backups, basic firewall and antivirus protection"
            }
        }
    }
    
    try:
        print_info("Sending request to API...")
        response = requests.post(
            f"{BASE_URL}/webhook/sheet-row",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Request accepted: {data['status']}")
            print_info(f"Request ID: {data['request_id']}")
            print_info(f"Company: {payload['company_name']}")
            print_info(f"Recipient: {payload['recipient_name']}")
            print_info(f"Email: {payload['recipient_email']}")
            
            print()
            print_warning("⏱️  Processing in background (~30-60 seconds):")
            print("   1. LLM analyzing your 9 departments...")
            print("   2. Generating PDF with bar chart and radar chart...")
            print("   3. Sending email with report...")
            print()
            print_info("📧 Check your email inbox (and spam folder) in about 1 minute!")
            
            return True
        else:
            print_error(f"Request failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("Could not connect to API")
        print_info("Make sure the application is running:")
        print("  python main.py")
        print("  OR")
        print("  docker-compose up -d")
        return False
        
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False

def show_department_mapping():
    """Display how your columns map to departments"""
    print("\n" + "="*70)
    print("YOUR GOOGLE SHEET COLUMNS → DEPARTMENT MAPPING")
    print("="*70 + "\n")
    
    departments = {
        "Leadership & Management": [
            "How do you track business performance metrics?",
            "How often do you analyze competitor activities?"
        ],
        "Customer Engagement": [
            "How do you handle customer inquiries?",
            "Average response time to customer queries"
        ],
        "Human Resources": [
            "How do you handle recruitment and screening?",
            "Employee attendance tracking method"
        ],
        "Sales & Marketing": [
            "How do you manage leads and follow-ups?",
            "Do you use any sales forecasting?",
            "How do you generate proposals/quotations?"
        ],
        "Operations": [
            "How are repetitive tasks currently handled?",
            "Process documentation and SOPs"
        ],
        "Inventory & Supply Chain": [
            "How do you track inventory levels?",
            "Vendor/supplier communication method"
        ],
        "Quality Control": [
            "How do you perform quality checks?",
            "Defect and complaint tracking"
        ],
        "Finance & Accounting": [
            "Invoice generation and management",
            "Expense tracking and approval"
        ],
        "IT & Technology": [
            "Do you have a company website?",
            "Data backup and security practices"
        ]
    }
    
    for dept, questions in departments.items():
        print(f"{Colors.BLUE}📊 {dept}{Colors.END}")
        for q in questions:
            print(f"   • {q}")
        print()

def main():
    """Main test function"""
    print("\n" + "="*70)
    print("AI Audit Agent - Test with YOUR Column Structure")
    print("="*70 + "\n")
    
    # Show mapping first
    show_department_mapping()
    
    # Test health
    print("="*70)
    print("STEP 1: Health Check")
    print("="*70 + "\n")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("API is healthy and ready!")
        else:
            print_error("API health check failed")
            return
    except Exception as e:
        print_error(f"Cannot connect to API: {e}")
        print_info("\nMake sure the application is running:")
        print("  python main.py")
        print("  OR")
        print("  docker-compose up -d")
        return
    
    # Test with your structure
    print("\n" + "="*70)
    print("STEP 2: Testing Audit Request")
    print("="*70 + "\n")
    
    success = test_with_your_structure()
    
    # Summary
    print("\n" + "="*70)
    if success:
        print_success("✨ TEST SUCCESSFUL!")
        print("="*70)
        print("\n📋 What's happening now:")
        print("  1. ✅ Webhook received and validated")
        print("  2. ⏳ LLM analyzing 9 departments (10-30s)")
        print("  3. ⏳ PDF generating with charts (5-10s)")
        print("  4. ⏳ Email sending (2-5s)")
        print("\n📧 You should receive an email in ~60 seconds!")
        print("\n💡 Next steps:")
        print("  • Check your email (and spam folder)")
        print("  • Review the PDF report")
        print("  • Verify all 9 departments are analyzed")
        print("  • Check the bar chart and radar chart")
        print("\n🔗 Then set up Google Sheets:")
        print("  • See: docs/GOOGLE_SHEETS_SETUP.md")
        print("  • Use: docs/gs_script_updated.txt")
    else:
        print_error("❌ TEST FAILED")
        print("="*70)
        print("\n🔍 Troubleshooting:")
        print("  1. Check if API is running: curl http://localhost:8000/health")
        print("  2. View logs: docker-compose logs -f")
        print("  3. Check .env configuration")
        print("  4. Verify HF_API_KEY and email settings")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\nTest interrupted by user")
    except Exception as e:
        print_error(f"\nUnexpected error: {str(e)}")
