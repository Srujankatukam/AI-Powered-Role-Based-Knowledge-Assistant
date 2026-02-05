"""
Example test script for AI Audit Agent
Run this to quickly test the application
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

def test_health_endpoint():
    """Test the health endpoint"""
    print_info("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check passed: {data['status']}")
            return True
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check failed: {str(e)}")
        return False

def test_webhook_valid():
    """Test webhook with valid data"""
    print_info("Testing webhook with valid data...")
    
    payload = {
        "company_name": "TechNova Solutions",
        "recipient_name": "Sarah Johnson",
        "recipient_email": "sarah@technova.com",
        "industry": "Information Technology",
        "company_size": "Medium (51-200 employees)",
        "annual_revenue_inr": "150 Cr",
        "departments": {
            "Leadership & Management": {
                "track_business_metrics": "Excel and manual reports",
                "competitor_analysis_frequency": "Quarterly",
                "strategic_planning": "Annual meetings"
            },
            "Customer Engagement": {
                "inquiry_handling": "Email and phone manually",
                "collect_feedback": "Surveys collected but not analyzed",
                "avg_response_time": "12-24 hours",
                "crm_system": "Basic spreadsheet tracking"
            },
            "Human Resources": {
                "recruitment_screening": "Manual CV review",
                "attendance_tracking": "Excel-based register",
                "performance_reviews": "Annual paper forms",
                "employee_engagement": "Quarterly surveys"
            },
            "IT & Technology": {
                "website": "Dynamic responsive website",
                "backup_security": "Weekly scheduled backups",
                "infrastructure": "Hybrid cloud and on-premise",
                "cybersecurity": "Basic firewall and antivirus"
            },
            "Operations": {
                "inventory_management": "Manual Excel tracking",
                "supply_chain": "Email-based supplier coordination",
                "quality_control": "Manual inspection processes"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/sheet-row",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Webhook accepted: {data['status']}")
            print_info(f"Request ID: {data['request_id']}")
            print_info(f"Message: {data['message']}")
            print_warning("Note: Processing happens in background. Check logs for completion.")
            return True
        else:
            print_error(f"Webhook failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Webhook test failed: {str(e)}")
        return False

def test_webhook_invalid():
    """Test webhook with invalid data"""
    print_info("Testing webhook with invalid data (should fail)...")
    
    payload = {
        "company_name": "Test Corp",
        "recipient_name": "John Doe",
        "recipient_email": "invalid-email",  # Invalid email
        "industry": "Tech"
        # Missing other required fields
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/sheet-row",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 422:
            print_success("Validation correctly rejected invalid data")
            return True
        else:
            print_error(f"Expected 422, got {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Invalid data test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("AI Audit Agent - Test Suite")
    print("="*60 + "\n")
    
    results = []
    
    # Test 1: Health endpoint
    results.append(("Health Check", test_health_endpoint()))
    print()
    
    # Test 2: Valid webhook
    results.append(("Valid Webhook", test_webhook_valid()))
    print()
    
    # Test 3: Invalid webhook
    results.append(("Invalid Webhook", test_webhook_invalid()))
    print()
    
    # Summary
    print("="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{test_name}: {status}{Colors.END}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("\n🎉 All tests passed!")
        return True
    else:
        print_error(f"\n❌ {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    print_info("Starting tests...")
    print_warning(f"Make sure the application is running at {BASE_URL}")
    print()
    
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print_warning("\n\nTests interrupted by user")
        exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {str(e)}")
        exit(1)
