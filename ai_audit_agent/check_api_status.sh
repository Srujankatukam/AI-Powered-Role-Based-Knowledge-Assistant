#!/bin/bash

# Quick API Status Checker
# Run this on the API server to diagnose issues

echo "========================================"
echo "AI Audit Agent - Status Check"
echo "========================================"
echo ""

# Check if API is running
echo "1. Checking if API is running..."
if pgrep -f "uvicorn main:app" > /dev/null || pgrep -f "docker-compose" > /dev/null; then
    echo "   ✅ Process found"
else
    echo "   ❌ API not running!"
    echo "   Start with: python main.py"
    echo "   Or: docker-compose up -d"
    exit 1
fi

echo ""
echo "2. Checking port 8000..."
if netstat -tulpn 2>/dev/null | grep -q ":8000 "; then
    echo "   ✅ Port 8000 is listening"
    netstat -tulpn 2>/dev/null | grep ":8000 " | head -1
else
    if command -v ss &> /dev/null; then
        if ss -tulpn 2>/dev/null | grep -q ":8000 "; then
            echo "   ✅ Port 8000 is listening"
            ss -tulpn 2>/dev/null | grep ":8000 " | head -1
        else
            echo "   ❌ Port 8000 not listening"
        fi
    else
        echo "   ⚠️  Cannot check (netstat/ss not available)"
    fi
fi

echo ""
echo "3. Testing health endpoint (localhost)..."
if command -v curl &> /dev/null; then
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null)
    if [ "$response" = "200" ]; then
        echo "   ✅ Health check passed (200 OK)"
        curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo ""
    else
        echo "   ❌ Health check failed (HTTP $response)"
    fi
else
    echo "   ⚠️  curl not installed, skipping"
fi

echo ""
echo "4. Checking local IP address..."
if command -v hostname &> /dev/null; then
    hostname -I 2>/dev/null | tr ' ' '\n' | grep -v "^$" | while read ip; do
        echo "   📍 $ip"
    done
fi

echo ""
echo "5. Testing webhook endpoint..."
if command -v curl &> /dev/null; then
    # Test with minimal valid data
    response=$(curl -s -X POST http://localhost:8000/webhook/sheet-row \
        -H "Content-Type: application/json" \
        -d '{
            "company_name": "Test",
            "recipient_name": "Test",
            "recipient_email": "test@test.com",
            "industry": "Test",
            "company_size": "Small",
            "annual_revenue_inr": "Test",
            "departments": {"IT": {"test": "test"}}
        }' 2>/dev/null)
    
    if echo "$response" | grep -q '"status":"accepted"'; then
        echo "   ✅ Webhook accepts POST requests"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    else
        echo "   ❌ Webhook returned error:"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    fi
else
    echo "   ⚠️  curl not installed, skipping"
fi

echo ""
echo "6. Checking firewall (if ufw installed)..."
if command -v ufw &> /dev/null; then
    status=$(sudo ufw status 2>/dev/null | grep -i "8000" || echo "Not configured")
    echo "   $status"
else
    echo "   ⚠️  ufw not installed, skipping"
fi

echo ""
echo "========================================"
echo "Summary"
echo "========================================"
echo ""
echo "If all checks passed:"
echo "  ✅ API is running correctly"
echo "  ✅ Try: python test_api_directly.py"
echo ""
echo "If webhook test failed:"
echo "  🔍 Check API logs for details"
echo "  📋 See: DIAGNOSIS.md"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo "  OR check terminal where python main.py is running"
echo ""
echo "========================================"
