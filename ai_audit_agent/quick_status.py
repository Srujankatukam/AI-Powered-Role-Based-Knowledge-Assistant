#!/usr/bin/env python3
"""
Quick status check - shows what's working and what's not
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check(test_name, condition, fix_hint=""):
    """Print check result"""
    if condition:
        print(f"✅ {test_name}")
        return True
    else:
        print(f"❌ {test_name}")
        if fix_hint:
            print(f"   Fix: {fix_hint}")
        return False

def main():
    print("=" * 70)
    print("🔍 AI AUDIT AGENT - QUICK STATUS CHECK")
    print("=" * 70)
    
    issues = []
    
    # Check 1: .env file
    print("\n1️⃣  Configuration Files")
    if check(".env file exists", os.path.exists(".env"), "Create: cp .env.example .env"):
        # Check email config
        sender = os.getenv("SENDER_EMAIL")
        password = os.getenv("SMTP_PASSWORD")
        
        has_sender = check(
            "SENDER_EMAIL configured", 
            sender and sender != "your-email@gmail.com",
            "Set real email in .env"
        )
        
        has_password = check(
            "SMTP_PASSWORD configured",
            password and password != "your_gmail_app_password_here",
            "Set Gmail app password in .env"
        )
        
        if not has_sender or not has_password:
            issues.append("Configure email credentials in .env")
        
        # Check LLM config
        use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
        
        if use_ollama:
            print(f"   Mode: Ollama")
            check(
                "OLLAMA_MODEL configured",
                os.getenv("OLLAMA_MODEL"),
                "Set OLLAMA_MODEL in .env"
            )
        else:
            print(f"   Mode: Hugging Face")
            if not check(
                "HF_API_KEY configured",
                os.getenv("HF_API_KEY"),
                "Set HF_API_KEY in .env"
            ):
                issues.append("Configure HF_API_KEY in .env")
    else:
        issues.append("Create .env file from .env.example")
    
    # Check 2: API running
    print("\n2️⃣  Application Status")
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        check("API is running on port 8000", response.status_code == 200)
    except:
        check("API is running on port 8000", False, "Start with: python main.py")
        issues.append("Start the application: python main.py")
    
    # Check 3: Ollama (if configured)
    use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
    if use_ollama:
        print("\n3️⃣  Ollama Status")
        try:
            import requests
            response = requests.get("http://localhost:11434", timeout=2)
            check("Ollama is running", response.status_code == 200, "Start with: ollama serve")
        except:
            check("Ollama is running", False, "Start with: ollama serve")
            issues.append("Start Ollama: ollama serve")
    
    # Check 4: Dependencies
    print("\n4️⃣  Python Dependencies")
    try:
        import fastapi
        check("fastapi installed", True)
    except:
        check("fastapi installed", False, "Install: pip install -r requirements.txt")
        issues.append("Install dependencies: pip install -r requirements.txt")
    
    try:
        import reportlab
        check("reportlab installed", True)
    except:
        check("reportlab installed", False, "Install: pip install -r requirements.txt")
    
    try:
        import matplotlib
        check("matplotlib installed", True)
    except:
        check("matplotlib installed", False, "Install: pip install -r requirements.txt")
    
    # Summary
    print("\n" + "=" * 70)
    if not issues:
        print("✅ ALL SYSTEMS READY!")
        print("\n📝 Next steps:")
        print("   1. If not running: python main.py")
        print("   2. Submit form in Google Sheets")
        print("   3. Check email in ~60 seconds")
    else:
        print(f"❌ FOUND {len(issues)} ISSUE(S):")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        print("\n🔧 FIX ISSUES ABOVE THEN RE-RUN THIS SCRIPT")
    print("=" * 70)

if __name__ == "__main__":
    main()
