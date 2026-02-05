#!/usr/bin/env python3
"""
Simple test of Hugging Face credentials using requests
"""

import requests
import json
import time

# Your credentials - REPLACE WITH YOUR ACTUAL KEY
API_KEY = "hf_YOUR_HUGGINGFACE_API_KEY_HERE"
ROUTER_URL = "https://router.huggingface.co/hf-inference/models/meta-llama/Meta-Llama-3-8B-Instruct"
STANDARD_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

def test_endpoint(url, name):
    """Test a specific endpoint"""
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('='*70)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": "Hello, this is a test. Please respond.",
        "parameters": {
            "max_new_tokens": 50,
            "temperature": 0.7
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        status = response.status_code
        
        print(f"Status Code: {status}")
        
        if status == 200:
            print("✅ SUCCESS!")
            try:
                result = response.json()
                print(f"Response preview: {json.dumps(result, indent=2)[:300]}")
                return True
            except:
                print(f"Response text: {response.text[:300]}")
                return True
        elif status == 503:
            print("⚠️  Model is loading... Response:")
            print(response.text[:200])
            return False
        elif status == 401:
            print("❌ Authentication failed - API key invalid")
            print(f"Response: {response.text}")
            return False
        elif status == 404:
            print("❌ Endpoint not found - URL might be wrong")
            print(f"Response: {response.text}")
            return False
        else:
            print(f"❌ Error: {status}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (30s)")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_with_company_data(url, name):
    """Test with company-specific data"""
    print(f"\n{'='*70}")
    print(f"Testing Customization: {name}")
    print('='*70)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Simple test prompt
    prompt = """Analyze this company and provide a brief summary:
Company Name: TechCorp Solutions
Industry: Technology
Size: Small (50 employees)

Provide a 2-sentence summary mentioning the company name."""
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.1
        }
    }
    
    try:
        print("Sending request...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        status = response.status_code
        
        print(f"Status Code: {status}")
        
        if status == 200:
            print("✅ SUCCESS!")
            result = response.json()
            
            # Extract response
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '')
            elif isinstance(result, dict):
                generated_text = result.get('generated_text', str(result))
            else:
                generated_text = str(result)
            
            print(f"\nGenerated Response:")
            print("-" * 70)
            print(generated_text[:500])
            print("-" * 70)
            
            # Check if customized
            if "TechCorp Solutions" in generated_text or "TechCorp" in generated_text:
                print("\n✅ Response mentions 'TechCorp' - CUSTOMIZED!")
                return True
            else:
                print("\n⚠️  Response doesn't mention company name")
                print("⚠️  Might be generic or need prompt adjustment")
                return False
        else:
            print(f"❌ Error: {status}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("="*70)
    print("TESTING YOUR HUGGING FACE CREDENTIALS")
    print("="*70)
    print(f"\nAPI Key: {API_KEY if API_KEY == 'hf_YOUR_HUGGINGFACE_API_KEY_HERE' else API_KEY[:20] + '...' + API_KEY[-10:]}")
    
    # Test 1: Router URL (your current setting)
    print("\n\n🔍 TEST 1: Your Router URL")
    result_router = test_endpoint(ROUTER_URL, "Router URL")
    
    if result_router:
        print("\n✅ Router URL is working!")
        test_with_company_data(ROUTER_URL, "Router URL")
    else:
        print("\n❌ Router URL failed")
    
    # Test 2: Standard URL (recommended)
    print("\n\n🔍 TEST 2: Standard API URL")
    result_standard = test_endpoint(STANDARD_URL, "Standard API URL")
    
    if result_standard:
        print("\n✅ Standard URL is working!")
        test_with_company_data(STANDARD_URL, "Standard URL")
    else:
        print("\n❌ Standard URL failed")
    
    # Summary
    print("\n\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    
    print(f"\nAPI Key: {'✅ Valid' if (result_router or result_standard) else '❌ Invalid or Rate Limited'}")
    print(f"Router URL: {'✅ Works' if result_router else '❌ Does not work'}")
    print(f"Standard URL: {'✅ Works' if result_standard else '❌ Does not work'}")
    
    print("\n" + "="*70)
    print("RECOMMENDATION")
    print("="*70)
    
    if result_router:
        print("\n✅ Keep your current settings - Router URL works fine!")
        print("\nYour .env is correct:")
        print("  HF_API_KEY=hf_YOUR_KEY_HERE")
        print("  HF_MODEL_URL=https://router.huggingface.co/hf-inference/models/meta-llama/Meta-Llama-3-8B-Instruct")
    elif result_standard:
        print("\n⚠️  Router URL doesn't work, but Standard URL does!")
        print("\n📝 UPDATE your .env to:")
        print("  HF_API_KEY=hf_YOUR_KEY_HERE")
        print("  HF_MODEL_URL=https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct")
        print("\nThen restart: docker-compose restart")
    else:
        print("\n❌ Neither URL works!")
        print("\nPossible causes:")
        print("  1. Model is loading (first time) - wait 30 seconds and retry")
        print("  2. API rate limit exceeded - wait a few minutes")
        print("  3. Hugging Face service issue - check status.huggingface.co")
        print("\nTry again in 30 seconds:")
        print("  python test_hf_credentials.py")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
