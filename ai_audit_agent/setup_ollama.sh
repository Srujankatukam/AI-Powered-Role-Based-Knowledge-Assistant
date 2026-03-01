#!/bin/bash

# Quick setup script for Ollama

echo "=========================================="
echo "🦙 Ollama Setup for AI Audit Agent"
echo "=========================================="
echo ""

# Check if Ollama is installed
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
else
    echo "📥 Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    
    if [ $? -eq 0 ]; then
        echo "✅ Ollama installed successfully"
    else
        echo "❌ Failed to install Ollama"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Starting Ollama Service"
echo "=========================================="
echo ""

# Check if Ollama is already running
if pgrep -x "ollama" > /dev/null; then
    echo "✅ Ollama is already running"
else
    echo "Starting Ollama in background..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
    
    if pgrep -x "ollama" > /dev/null; then
        echo "✅ Ollama started successfully"
    else
        echo "❌ Failed to start Ollama"
        echo "Try manually: ollama serve"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Downloading Llama 3 Model"
echo "=========================================="
echo ""

# Check if llama3 is already downloaded
if ollama list | grep -q "llama3"; then
    echo "✅ Llama 3 is already downloaded"
else
    echo "📥 Downloading Llama 3 (this may take a few minutes)..."
    ollama pull llama3
    
    if [ $? -eq 0 ]; then
        echo "✅ Llama 3 downloaded successfully"
    else
        echo "❌ Failed to download Llama 3"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Updating .env Configuration"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

# Update .env file
if grep -q "USE_OLLAMA" .env; then
    sed -i.bak 's/USE_OLLAMA=false/USE_OLLAMA=true/' .env
    sed -i.bak 's/# USE_OLLAMA=true/USE_OLLAMA=true/' .env
    echo "✅ Updated USE_OLLAMA in .env"
else
    echo "USE_OLLAMA=true" >> .env
    echo "OLLAMA_MODEL=llama3" >> .env
    echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env
    echo "✅ Added Ollama configuration to .env"
fi

echo ""
echo "=========================================="
echo "Testing Ollama"
echo "=========================================="
echo ""

if command -v python3 &> /dev/null; then
    python3 test_ollama.py
elif command -v python &> /dev/null; then
    python test_ollama.py
else
    echo "⚠️  Python not found, skipping test"
fi

echo ""
echo "=========================================="
echo "✅ SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "Ollama is now configured and running!"
echo ""
echo "Next steps:"
echo "  1. Restart your application:"
echo "     docker-compose restart"
echo "     OR"
echo "     python main.py"
echo ""
echo "  2. Test the integration:"
echo "     python test_llm_directly.py"
echo ""
echo "  3. Send a test audit request:"
echo "     python test_api_directly.py"
echo ""
echo "=========================================="
echo ""
echo "Model: llama3"
echo "URL: http://localhost:11434"
echo "Status: ✅ Ready"
echo ""
echo "=========================================="
