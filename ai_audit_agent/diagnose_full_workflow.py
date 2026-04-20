#!/usr/bin/env python3
"""
Complete workflow diagnostic - finds where the failure is happening
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()

def print_header(text):
    print("\n" + "="*70)
    print(text)
    print("="*70)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def print_info(text):
    print(f"ℹ️  {text}")

async def test_full_workflow():
    """Test each component of the workflow"""
    
    print_header("🔍 AI AUDIT AGENT - FULL WORKFLOW DIAGNOSTIC")
    
    # Test 1: Environment Configuration
    print_header("1. Environment Configuration")
    
    use_ollama = os.getenv("USE_OLLAMA", "false")
    print(f"USE_OLLAMA: {use_ollama}")
    
    if use_ollama.lower() == "true":
        print_info("Mode: Ollama (Local)")
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        print(f"  Model: {ollama_model}")
        print(f"  URL: {ollama_url}")
    else:
        print_info("Mode: Hugging Face (Cloud)")
        hf_key = os.getenv("HF_API_KEY", "")
        if hf_key:
            print_success("HF_API_KEY is set")
        else:
            print_error("HF_API_KEY is NOT set")
    
    sender_email = os.getenv("SENDER_EMAIL", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    
    print(f"\nEmail Configuration:")
    print(f"  SENDER_EMAIL: {'Set' if sender_email else 'NOT SET ❌'}")
    print(f"  SMTP_PASSWORD: {'Set' if smtp_password else 'NOT SET ❌'}")
    
    if not sender_email or not smtp_password:
        print_error("Email credentials missing - emails will NOT be sent!")
    
    # Test 2: LLM Client
    print_header("2. Testing LLM Client")
    
    try:
        from llm_client import LLMClient
        client = LLMClient()
        
        if client.use_ollama:
            print_success("LLM Client initialized in Ollama mode")
            
            # Test Ollama connection
            import requests
            try:
                response = requests.get("http://localhost:11434", timeout=2)
                if response.status_code == 200:
                    print_success("Ollama is running")
                else:
                    print_error("Ollama is not responding correctly")
            except:
                print_error("Cannot connect to Ollama - is it running?")
                print_info("Start with: ollama serve")
        else:
            print_info("LLM Client initialized in Hugging Face mode")
        
        # Test LLM generation
        print_info("Testing LLM generation...")
        test_data = {
            "company_name": "DiagnosticTest Corp",
            "industry": "Testing",
            "company_size": "Small",
            "annual_revenue_inr": "10 Cr",
            "departments": {"IT": {"website": "Basic"}}
        }
        
        result = await client.generate_audit_analysis(test_data)
        
        if result:
            summary = result.get('summary', {}).get('personalized_summary', '')
            if 'DiagnosticTest Corp' in summary or len(summary) > 100:
                print_success("LLM generated customized response!")
                print(f"  Summary length: {len(summary)} chars")
            else:
                print_warning("LLM might be using fallback response")
                print(f"  Summary: {summary[:100]}...")
        else:
            print_error("LLM returned None - check logs")
            
    except Exception as e:
        print_error(f"LLM Client error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: PDF Builder
    print_header("3. Testing PDF Builder")
    
    try:
        from pdf_builder import PDFBuilder
        builder = PDFBuilder()
        print_success("PDF Builder initialized")
        
        # Test PDF creation
        test_company_data = {
            "company_name": "PDF Test Corp",
            "recipient_name": "Test User",
            "recipient_email": "test@test.com",
            "industry": "Testing",
            "company_size": "Small",
            "annual_revenue_inr": "10 Cr"
        }
        
        test_llm_analysis = {
            "summary": {
                "personalized_summary": "Test summary for PDF Test Corp.",
                "overall_risk_score": 65,
                "ai_maturity_level": "Medium"
            },
            "sections": [
                {
                    "section_name": "IT",
                    "level": "Medium",
                    "drawbacks": [{"title": "Test", "details": "Test details"}]
                }
            ]
        }
        
        print_info("Generating test PDF...")
        pdf_path = builder.create_report(test_company_data, test_llm_analysis, "test_123")
        
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print_success(f"PDF created successfully!")
            print(f"  Path: {pdf_path}")
            print(f"  Size: {file_size / 1024:.1f} KB")
            
            # Cleanup
            os.remove(pdf_path)
            print_info("Test PDF cleaned up")
        else:
            print_error("PDF file was not created")
            
    except Exception as e:
        print_error(f"PDF Builder error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Email Service
    print_header("4. Testing Email Service")
    
    try:
        from mailer import EmailService
        email_service = EmailService()
        
        if email_service.enabled:
            print_success("Email service initialized and enabled")
            print(f"  Sender: {email_service.sender_email}")
            print(f"  SMTP: {email_service.smtp_host}:{email_service.smtp_port}")
            
            # Test connection
            print_info("Testing SMTP connection...")
            if email_service.test_connection():
                print_success("SMTP connection successful!")
            else:
                print_error("SMTP connection failed - check credentials")
        else:
            print_error("Email service is DISABLED")
            print_warning("Emails will NOT be sent!")
            print_info("Fix: Set SENDER_EMAIL and SMTP_PASSWORD in .env")
            
    except Exception as e:
        print_error(f"Email Service error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: API Endpoint
    print_header("5. Testing API Endpoint")
    
    try:
        import requests
        
        # Test health
        print_info("Testing /health endpoint...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print_success("API is running and healthy!")
        else:
            print_error(f"API health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API on localhost:8000")
        print_warning("Is the application running?")
        print_info("Start with: python main.py")
        return
    except Exception as e:
        print_error(f"API test error: {e}")
        return
    
    # Test 6: Full webhook test
    print_header("6. Testing Full Webhook")
    
    try:
        import requests
        
        test_payload = {
            "company_name": "Workflow Test Corp",
            "recipient_name": "Test User",
            "recipient_email": os.getenv("SENDER_EMAIL", "test@test.com"),
            "industry": "Testing",
            "company_size": "Small",
            "annual_revenue_inr": "10 Cr",
            "departments": {
                "IT": {"website": "Basic", "backup_security": "None"}
            }
        }
        
        print_info(f"Sending webhook request...")
        print(f"  Email will be sent to: {test_payload['recipient_email']}")
        
        response = requests.post(
            "http://localhost:8000/webhook/sheet-row",
            json=test_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Webhook accepted!")
            print(f"  Request ID: {result.get('request_id')}")
            print(f"  Status: {result.get('status')}")
            
            print_info("\n⏱️  Background processing started...")
            print("  This happens asynchronously. Check:")
            print("  1. Application logs for progress")
            print("  2. Email inbox in ~60 seconds")
            print("  3. /tmp folder for generated PDF")
        else:
            print_error(f"Webhook failed: {response.status_code}")
            print(f"  Response: {response.text}")
            
    except Exception as e:
        print_error(f"Webhook test error: {e}")
    
    # Final Summary
    print_header("📋 DIAGNOSTIC SUMMARY")
    
    issues = []
    
    if use_ollama.lower() == "true":
        try:
            import requests
            requests.get("http://localhost:11434", timeout=2)
        except:
            issues.append("Ollama not running - start with: ollama serve")
    else:
        if not os.getenv("HF_API_KEY"):
            issues.append("HF_API_KEY not set in .env")
    
    if not sender_email or not smtp_password:
        issues.append("Email credentials not configured - emails won't be sent")
    
    try:
        import requests
        requests.get("http://localhost:8000/health", timeout=2)
    except:
        issues.append("API not running - start with: python main.py")
    
    if issues:
        print("\n❌ Issues Found:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        
        print("\n🔧 Quick Fix:")
        for issue in issues:
            if "Ollama" in issue:
                print("  → Terminal 1: ollama serve")
                print("  → Terminal 2: ollama pull llama3")
            elif "HF_API_KEY" in issue:
                print("  → Add HF_API_KEY to .env")
            elif "Email" in issue:
                print("  → Add SENDER_EMAIL and SMTP_PASSWORD to .env")
            elif "API not running" in issue:
                print("  → Terminal: python main.py")
    else:
        print("\n✅ All systems operational!")
        print("\n📧 To test full workflow:")
        print("  1. Application is running")
        print("  2. Send test request (already sent above)")
        print("  3. Wait 60 seconds")
        print("  4. Check email inbox")
        print("  5. Look for PDF in /tmp folder")

if __name__ == "__main__":
    try:
        asyncio.run(test_full_workflow())
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
