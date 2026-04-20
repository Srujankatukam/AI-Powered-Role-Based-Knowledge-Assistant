#!/usr/bin/env python3
"""
Test Ollama installation and connection
"""

import requests
import json

OLLAMA_URL = "http://localhost:11434"

def test_ollama_running():
    """Test if Ollama is running"""
    print("="*70)
    print("Testing Ollama Installation")
    print("="*70)
    
    try:
        response = requests.get(OLLAMA_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running!")
            return True
        else:
            print(f"⚠️  Ollama responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama")
        print("\nTo fix:")
        print("  1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh")
        print("  2. Start Ollama: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_list_models():
    """List available models"""
    print("\n" + "="*70)
    print("Checking Available Models")
    print("="*70)
    
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            if models:
                print(f"✅ Found {len(models)} model(s):")
                for model in models:
                    name = model.get('name', 'unknown')
                    size = model.get('size', 0) / (1024**3)  # Convert to GB
                    print(f"  - {name} ({size:.1f} GB)")
                return True
            else:
                print("⚠️  No models downloaded")
                print("\nTo download Llama 3:")
                print("  ollama pull llama3")
                return False
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_model_inference(model_name="llama3"):
    """Test model inference"""
    print("\n" + "="*70)
    print(f"Testing Model: {model_name}")
    print("="*70)
    
    payload = {
        "model": model_name,
        "prompt": "Hello! Please respond with a short greeting.",
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 50
        }
    }
    
    try:
        print("Sending test prompt...")
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '')
            
            print("✅ Model response received!")
            print(f"\nGenerated text:")
            print("-" * 70)
            print(generated_text[:200])
            print("-" * 70)
            
            # Check performance
            eval_count = result.get('eval_count', 0)
            eval_duration = result.get('eval_duration', 0) / 1e9  # Convert to seconds
            
            if eval_count > 0 and eval_duration > 0:
                tokens_per_sec = eval_count / eval_duration
                print(f"\nPerformance: {tokens_per_sec:.1f} tokens/second")
            
            return True
        elif response.status_code == 404:
            print(f"❌ Model '{model_name}' not found")
            print(f"\nTo download:")
            print(f"  ollama pull {model_name}")
            return False
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (model might be loading)")
        print("Try again in a few seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_audit_prompt(model_name="llama3"):
    """Test with audit-style prompt"""
    print("\n" + "="*70)
    print("Testing with Audit Prompt")
    print("="*70)
    
    prompt = """Analyze this company and provide a brief assessment:

Company: TechCorp Solutions
Industry: Technology
Size: Small (50 employees)
IT Infrastructure: Basic website, no backup systems

Provide a 2-sentence assessment mentioning the company name and key risks."""
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 200
        }
    }
    
    try:
        print("Sending audit prompt...")
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '')
            
            print("✅ Response received!")
            print(f"\nAssessment:")
            print("-" * 70)
            print(generated_text)
            print("-" * 70)
            
            # Check if it mentions company name
            if "TechCorp" in generated_text:
                print("\n✅ Response mentions company name - GOOD!")
            else:
                print("\n⚠️  Response doesn't mention company name")
            
            return True
        else:
            print(f"❌ Error: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n🦙 OLLAMA DIAGNOSTIC TOOL\n")
    
    # Test 1: Check if Ollama is running
    if not test_ollama_running():
        print("\n" + "="*70)
        print("❌ Ollama is not running. Please start it first.")
        print("="*70)
        return
    
    # Test 2: List models
    has_models = test_list_models()
    
    if not has_models:
        print("\n" + "="*70)
        print("⚠️  No models available. Download one first:")
        print("  ollama pull llama3")
        print("="*70)
        return
    
    # Test 3: Test inference
    model_name = input("\nWhich model to test? (default: llama3): ").strip() or "llama3"
    test_model_inference(model_name)
    
    # Test 4: Test audit prompt
    test_audit_prompt(model_name)
    
    # Summary
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED")
    print("="*70)
    print("\nYour Ollama setup is ready!")
    print("\nNext steps:")
    print("  1. Update .env: USE_OLLAMA=true")
    print("  2. Update .env: OLLAMA_MODEL=" + model_name)
    print("  3. Restart app: docker-compose restart")
    print("  4. Test: python test_llm_directly.py")
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
