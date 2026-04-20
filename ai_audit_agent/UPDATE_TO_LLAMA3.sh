#!/bin/bash

# Quick update script to switch to Llama 3
# Run this if you're already using the old version

echo "=========================================="
echo "Updating AI Audit Agent to Llama 3"
echo "=========================================="
echo ""

# Check if .env exists
if [ -f ".env" ]; then
    echo "✓ Found .env file"
    
    # Check if HF_MODEL_URL is set
    if grep -q "HF_MODEL_URL" .env; then
        echo "Updating HF_MODEL_URL to Llama 3..."
        
        # Backup .env
        cp .env .env.backup
        echo "✓ Backed up .env to .env.backup"
        
        # Update or add HF_MODEL_URL
        if grep -q "HF_MODEL_URL=" .env; then
            # Update existing line
            sed -i.tmp 's|HF_MODEL_URL=.*|HF_MODEL_URL=https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct|' .env
            rm -f .env.tmp
            echo "✓ Updated HF_MODEL_URL to Llama 3"
        else
            # Add new line
            echo "HF_MODEL_URL=https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct" >> .env
            echo "✓ Added HF_MODEL_URL for Llama 3"
        fi
    else
        echo "✓ HF_MODEL_URL not in .env (will use default Llama 3)"
    fi
else
    echo "⚠ .env file not found"
    echo "Creating from .env.example..."
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ Created .env from .env.example"
        echo ""
        echo "⚠ IMPORTANT: Edit .env and add your API keys!"
    else
        echo "✗ .env.example not found"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Restarting Application"
echo "=========================================="
echo ""

# Check if Docker is being used
if [ -f "docker-compose.yml" ]; then
    echo "Detected Docker setup..."
    
    if docker-compose ps | grep -q "Up"; then
        echo "Restarting Docker containers..."
        docker-compose down
        docker-compose up -d
        echo "✓ Docker containers restarted"
    else
        echo "Starting Docker containers..."
        docker-compose up -d
        echo "✓ Docker containers started"
    fi
else
    echo "⚠ Docker Compose not found"
    echo "If running directly with Python, restart with:"
    echo "  python main.py"
fi

echo ""
echo "=========================================="
echo "Testing Update"
echo "=========================================="
echo ""

# Wait a moment for server to start
sleep 3

# Test health endpoint
if command -v curl &> /dev/null; then
    echo "Testing API health..."
    response=$(curl -s http://localhost:8000/health 2>/dev/null)
    
    if echo "$response" | grep -q "ok"; then
        echo "✓ API is healthy!"
        echo ""
        echo "✅ Update complete!"
        echo ""
        echo "Your system is now using Llama 3 8B Instruct"
        echo ""
        echo "Next steps:"
        echo "  1. Test: python test_with_your_columns.py"
        echo "  2. Try a Google Sheets trigger"
        echo "  3. Check email for improved report quality"
        echo ""
        echo "See LLAMA3_UPDATE.md for details on improvements"
    else
        echo "⚠ API not responding"
        echo "Check logs: docker-compose logs -f"
    fi
else
    echo "⚠ curl not installed, cannot test"
    echo "Manually test: curl http://localhost:8000/health"
fi

echo ""
echo "=========================================="
