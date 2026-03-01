#!/usr/bin/env python3
"""
Check if Ollama is properly integrated and configured
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("="*70)
print("🔍 Checking Ollama Integration")
print("="*70)

# Check environment variables
print("\n1. Checking .env configuration...")

use_ollama = os.getenv("USE_OLLAMA", "false")
ollama_model = os.getenv("OLLAMA_MODEL", "not set")
ollama_url = os.getenv("OLLAMA_BASE_URL", "not set")
hf_key = os.getenv("HF_API_KEY", "not set")

print(f"   USE_OLLAMA: {use_ollama}")

if use_ollama.lower() == "true":
    print("   ✅ Ollama mode is ENABLED")
    print(f"   Model: {ollama_model}")
    print(f"   URL: {ollama_url}")
else:
    print("   ❌ Ollama mode is DISABLED")
    print("   Currently using: Hugging Face")
    print(f"   HF_API_KEY: {'Set' if hf_key != 'not set' else 'NOT SET'}")

# Check if Ollama is running
print("\n2. Checking if Ollama is running...")
try:
    import requests
    response = requests.get("http://localhost:11434", timeout=2)
    if response.status_code == 200:
        print("   ✅ Ollama is running!")
    else:
        print(f"   ⚠️  Ollama responded with status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ❌ Ollama is NOT running!")
    print("   Start with: ollama serve")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check if model is downloaded
print("\n3. Checking if model is downloaded...")
try:
    import subprocess
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
    if 'llama3' in result.stdout:
        print("   ✅ llama3 model is downloaded")
        print(f"   Models: {[line.split()[0] for line in result.stdout.split('\\n')[1:] if line.strip()]}")
    else:
        print("   ❌ llama3 model NOT downloaded")
        print("   Download with: ollama pull llama3")
except FileNotFoundError:
    print("   ❌ Ollama not installed")
    print("   Install with: curl -fsSL https://ollama.com/install.sh | sh")
except Exception as e:
    print(f"   ⚠️  Could not check: {e}")

# Test LLM client initialization
print("\n4. Testing LLM client initialization...")
try:
    from llm_client import LLMClient
    client = LLMClient()
    
    if client.use_ollama:
        print("   ✅ LLM Client initialized in OLLAMA mode")
        print(f"   Model: {client.ollama_model}")
        print(f"   URL: {client.ollama_base_url}")
    else:
        print("   ⚠️  LLM Client initialized in HUGGING FACE mode")
        print("   To use Ollama, set USE_OLLAMA=true in .env")
except Exception as e:
    print(f"   ❌ Error initializing client: {e}")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

if use_ollama.lower() == "true":
    print("\n✅ Configuration says: Use Ollama")
    
    # Check if everything is ready
    try:
        import requests
        requests.get("http://localhost:11434", timeout=2)
        ollama_running = True
    except:
        ollama_running = False
    
    if ollama_running:
        print("✅ Ollama is running")
        print("\n🎯 Everything looks good!")
        print("\nNext steps:")
        print("  1. Restart your app: python main.py")
        print("  2. Test endpoint: python test_api_directly.py")
        print("  3. Should now use Ollama (fast & free!)")
    else:
        print("❌ Ollama is NOT running")
        print("\n🔧 To fix:")
        print("  1. Start Ollama: ollama serve")
        print("  2. In new terminal: ollama pull llama3")
        print("  3. Then restart app: python main.py")
else:
    print("\n⚠️  Configuration says: Use Hugging Face")
    print("\n🔧 To switch to Ollama:")
    print("  1. Update .env: USE_OLLAMA=true")
    print("  2. Or run: bash setup_ollama.sh")
    print("  3. Restart app: python main.py")

print("\n" + "="*70)
