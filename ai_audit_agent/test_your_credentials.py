#!/usr/bin/env python3
"""
Test your specific Hugging Face credentials
"""

import asyncio
import aiohttp
import json

# Your credentials - REPLACE WITH YOUR ACTUAL KEY
API_KEY = "hf_YOUR_HUGGINGFACE_API_KEY_HERE"
ROUTER_URL = "https://router.huggingface.co/hf-inference/models/meta-llama/Meta-Llama-3-8B-Instruct"
STANDARD_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

async def test_endpoint(url, name):
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
        "inputs": "Hello, how are you?",
        "parameters": {
            "max_new_tokens": 50,
            "temperature": 0.1
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                status = response.status
                text = await response.text()
                
                print(f"Status Code: {status}")
                
                if status == 200:
                    print("✅ SUCCESS!")
                    try:
                        result = json.loads(text)
                        print(f"Response: {json.dumps(result, indent=2)[:500]}")
                        return True
                    except:
                        print(f"Response: {text[:500]}")
                        return True
                elif status == 503:
                    print("⚠️  Model is loading... wait 20 seconds and retry")
                    return False
                elif status == 401:
                    print("❌ Authentication failed - API key invalid")
                    return False
                elif status == 404:
                    print("❌ Endpoint not found - URL might be wrong")
                    return False
                else:
                    print(f"❌ Error: {status}")
                    print(f"Response: {text}")
                    return False
                    
    except asyncio.TimeoutError:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_with_audit_prompt(url, name):
    """Test with actual audit prompt"""
    print(f"\n{'='*70}")
    print(f"Testing with Audit Prompt: {name}")
    print('='*70)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are an AI auditor. Return only valid JSON.<|eot_id|><|start_header_id|>user<|end_header_id|>

Analyze this company and return JSON:
- Company: TestCorp
- Industry: Technology
- Size: Small

Return JSON with summary and risk_score.<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.1,
            "do_sample": True,
            "return_full_text": False,
            "stop": ["<|eot_id|>", "<|end_of_text|>"]
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                status = response.status
                text = await response.text()
                
                print(f"Status Code: {status}")
                
                if status == 200:
                    print("✅ SUCCESS!")
                    print(f"Response length: {len(text)} chars")
                    print(f"Response preview:\n{text[:500]}")
                    
                    # Check if it looks like valid output
                    if "TestCorp" in text or "Technology" in text:
                        print("\n✅ Response mentions company details!")
                    else:
                        print("\n⚠️  Response doesn't mention company - might need prompt tuning")
                    
                    return True
                else:
                    print(f"❌ Error: {status}")
                    print(f"Response: {text[:500]}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    print("="*70)
    print("TESTING YOUR HUGGING FACE CREDENTIALS")
    print("="*70)
    print(f"\nAPI Key: {API_KEY[:20]}...{API_KEY[-10:]}")
    print(f"Router URL: {ROUTER_URL}")
    print(f"Standard URL: {STANDARD_URL}")
    
    # Test 1: Your router URL
    result1 = await test_endpoint(ROUTER_URL, "Your Router URL")
    
    # Test 2: Standard URL
    result2 = await test_endpoint(STANDARD_URL, "Standard API URL")
    
    # Test 3: With audit prompt on working endpoint
    if result1:
        await test_with_audit_prompt(ROUTER_URL, "Router URL with Audit Prompt")
    elif result2:
        await test_with_audit_prompt(STANDARD_URL, "Standard URL with Audit Prompt")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if result1:
        print("✅ Your router URL works!")
        print("   Keep using: router.huggingface.co")
    elif result2:
        print("⚠️  Router URL doesn't work, but standard URL does")
        print("   RECOMMENDATION: Change .env to use:")
        print("   HF_MODEL_URL=https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct")
    else:
        print("❌ Neither URL works")
        print("   Possible issues:")
        print("   - API key invalid")
        print("   - Model loading (wait and retry)")
        print("   - Rate limit exceeded")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    asyncio.run(main())
