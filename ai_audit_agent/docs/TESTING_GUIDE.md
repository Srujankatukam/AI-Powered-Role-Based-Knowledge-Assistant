# AI Audit Agent - Testing Guide

Comprehensive guide for testing the AI Audit Agent application.

## 🧪 Testing Checklist

- [ ] Health endpoint responds correctly
- [ ] Webhook accepts valid requests
- [ ] Webhook rejects invalid requests
- [ ] LLM integration works
- [ ] PDF generation succeeds
- [ ] Charts are created
- [ ] Email delivery works
- [ ] Background processing completes
- [ ] Error handling works
- [ ] Logging is functional

---

## 🔍 Manual Testing

### 1. Test Health Endpoint

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00.123456",
  "service": "AI Audit Agent"
}
```

### 2. Test Webhook with Valid Data

```bash
curl -X POST http://localhost:8000/webhook/sheet-row \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Corporation",
    "recipient_name": "John Doe",
    "recipient_email": "john@testcorp.com",
    "industry": "Technology",
    "company_size": "Medium (51-200 employees)",
    "annual_revenue_inr": "100 Cr",
    "departments": {
      "IT & Technology": {
        "infrastructure": "Cloud-based",
        "security": "Advanced firewall"
      },
      "Human Resources": {
        "recruitment": "Manual screening",
        "attendance": "Biometric system"
      }
    }
  }'
```

**Expected Response:**
```json
{
  "status": "accepted",
  "message": "Audit request accepted and being processed for Test Corporation",
  "request_id": "audit_20240115_103000",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

### 3. Test with Invalid Data

**Missing Required Field:**
```bash
curl -X POST http://localhost:8000/webhook/sheet-row \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Corp",
    "recipient_name": "John Doe"
  }'
```

**Expected Response:** 422 Unprocessable Entity

**Invalid Email:**
```bash
curl -X POST http://localhost:8000/webhook/sheet-row \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Corp",
    "recipient_name": "John Doe",
    "recipient_email": "invalid-email",
    "industry": "Tech",
    "company_size": "Small",
    "annual_revenue_inr": "50 Cr",
    "departments": {"IT": {"test": "value"}}
  }'
```

**Expected Response:** 422 Unprocessable Entity with email validation error

---

## 🐍 Automated Testing with Python

### Setup Test Environment

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Create tests directory
mkdir tests
```

### Test File: `tests/test_api.py`

```python
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert data["service"] == "AI Audit Agent"

@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

@pytest.mark.asyncio
async def test_webhook_valid_request():
    """Test webhook with valid data"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "company_name": "Test Corp",
            "recipient_name": "John Doe",
            "recipient_email": "john@testcorp.com",
            "industry": "Technology",
            "company_size": "Medium (51-200 employees)",
            "annual_revenue_inr": "100 Cr",
            "departments": {
                "IT": {
                    "infrastructure": "Cloud"
                }
            }
        }
        response = await client.post("/webhook/sheet-row", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert "request_id" in data
        assert "Test Corp" in data["message"]

@pytest.mark.asyncio
async def test_webhook_missing_field():
    """Test webhook with missing required field"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "company_name": "Test Corp",
            "recipient_name": "John Doe"
            # Missing other required fields
        }
        response = await client.post("/webhook/sheet-row", json=payload)
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_webhook_invalid_email():
    """Test webhook with invalid email"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "company_name": "Test Corp",
            "recipient_name": "John Doe",
            "recipient_email": "invalid-email",
            "industry": "Tech",
            "company_size": "Small",
            "annual_revenue_inr": "50 Cr",
            "departments": {"IT": {"test": "value"}}
        }
        response = await client.post("/webhook/sheet-row", json=payload)
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_webhook_empty_departments():
    """Test webhook with empty departments"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "company_name": "Test Corp",
            "recipient_name": "John Doe",
            "recipient_email": "john@testcorp.com",
            "industry": "Tech",
            "company_size": "Small",
            "annual_revenue_inr": "50 Cr",
            "departments": {}
        }
        response = await client.post("/webhook/sheet-row", json=payload)
        assert response.status_code == 422
```

### Run Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_api.py::test_health_endpoint
```

---

## 🔬 Component Testing

### Test LLM Client

```python
# test_llm_client.py
import asyncio
from llm_client import LLMClient

async def test_llm():
    client = LLMClient()
    
    test_data = {
        "company_name": "Test Corp",
        "industry": "Technology",
        "company_size": "Medium",
        "annual_revenue_inr": "100 Cr",
        "departments": {
            "IT": {
                "infrastructure": "Cloud-based"
            }
        }
    }
    
    result = await client.generate_audit_analysis(test_data)
    
    print("LLM Response:")
    print(result)
    
    assert result is not None
    assert "summary" in result
    assert "sections" in result

if __name__ == "__main__":
    asyncio.run(test_llm())
```

Run:
```bash
python test_llm_client.py
```

### Test PDF Builder

```python
# test_pdf_builder.py
from pdf_builder import PDFBuilder

def test_pdf_generation():
    builder = PDFBuilder()
    
    company_data = {
        "company_name": "Test Corporation",
        "recipient_name": "John Doe",
        "recipient_email": "john@testcorp.com",
        "industry": "Technology",
        "company_size": "Medium",
        "annual_revenue_inr": "100 Cr",
        "departments": {}
    }
    
    llm_analysis = {
        "summary": {
            "personalized_summary": "Test summary here.",
            "overall_risk_score": 65,
            "ai_maturity_level": "Medium"
        },
        "sections": [
            {
                "section_name": "IT",
                "level": "High",
                "drawbacks": [
                    {
                        "title": "Test Issue",
                        "details": "Test details here."
                    }
                ]
            }
        ]
    }
    
    pdf_path = builder.create_report(
        company_data=company_data,
        llm_analysis=llm_analysis,
        request_id="test_123"
    )
    
    print(f"PDF created at: {pdf_path}")
    
    import os
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0
    
    print("✓ PDF generation successful")

if __name__ == "__main__":
    test_pdf_generation()
```

Run:
```bash
python test_pdf_builder.py
```

### Test Email Service

```python
# test_mailer.py
from mailer import EmailService

def test_email_connection():
    service = EmailService()
    
    if service.enabled:
        result = service.test_connection()
        
        if result:
            print("✓ Email service connection successful")
        else:
            print("✗ Email service connection failed")
    else:
        print("⚠ Email service not configured")

if __name__ == "__main__":
    test_email_connection()
```

Run:
```bash
python test_mailer.py
```

---

## 🎭 Integration Testing

### Full Workflow Test

```python
# test_full_workflow.py
import asyncio
import time
from httpx import AsyncClient
from main import app

async def test_full_workflow():
    """Test complete audit workflow"""
    
    async with AsyncClient(app=app, base_url="http://test", timeout=180.0) as client:
        # Send audit request
        payload = {
            "company_name": "Integration Test Corp",
            "recipient_name": "Test User",
            "recipient_email": "test@example.com",
            "industry": "Technology",
            "company_size": "Large",
            "annual_revenue_inr": "500 Cr",
            "departments": {
                "IT": {"infrastructure": "Cloud"},
                "HR": {"recruitment": "Manual"}
            }
        }
        
        print("1. Sending audit request...")
        response = await client.post("/webhook/sheet-row", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        request_id = data["request_id"]
        print(f"✓ Request accepted: {request_id}")
        
        # Wait for processing
        print("2. Waiting for background processing...")
        await asyncio.sleep(60)  # Wait for LLM + PDF + Email
        
        print("✓ Integration test completed")

if __name__ == "__main__":
    asyncio.run(test_full_workflow())
```

Run:
```bash
python test_full_workflow.py
```

---

## 📊 Load Testing

### Using Apache Bench

```bash
# Install
sudo apt install apache2-utils

# Simple load test
ab -n 100 -c 10 http://localhost:8000/health

# Webhook load test (create test.json first)
ab -n 10 -c 2 -p test.json -T application/json http://localhost:8000/webhook/sheet-row
```

### Using Locust

```python
# locustfile.py
from locust import HttpUser, task, between

class AuditUser(HttpUser):
    wait_time = between(1, 5)
    
    @task
    def health_check(self):
        self.client.get("/health")
    
    @task(3)
    def submit_audit(self):
        payload = {
            "company_name": "Load Test Corp",
            "recipient_name": "Test User",
            "recipient_email": "test@example.com",
            "industry": "Technology",
            "company_size": "Medium",
            "annual_revenue_inr": "100 Cr",
            "departments": {
                "IT": {"test": "value"}
            }
        }
        self.client.post("/webhook/sheet-row", json=payload)
```

Run:
```bash
pip install locust
locust -f locustfile.py --host=http://localhost:8000
# Open http://localhost:8089 in browser
```

---

## 🐛 Debugging Tips

### Enable Debug Logging

```python
# In main.py, change log level
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Check Docker Logs

```bash
# Follow logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs ai-audit-agent
```

### Test LLM Directly

```bash
curl -X POST https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1 \
  -H "Authorization: Bearer YOUR_HF_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": "Test prompt",
    "parameters": {
      "max_new_tokens": 100
    }
  }'
```

### Verify Email Settings

```python
import smtplib

server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.login('your-email@gmail.com', 'your-app-password')
print("✓ SMTP connection successful")
server.quit()
```

---

## ✅ Test Coverage Goals

- **Unit Tests**: 80%+ coverage
- **Integration Tests**: All workflows
- **API Tests**: All endpoints
- **Error Handling**: All error paths

---

## 📋 Pre-Deployment Checklist

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Health endpoint responds
- [ ] Webhook accepts valid requests
- [ ] Webhook rejects invalid requests
- [ ] LLM integration works
- [ ] PDF generation successful
- [ ] Email delivery works
- [ ] Error handling tested
- [ ] Load testing completed
- [ ] Security testing done
- [ ] Documentation reviewed

---

## 🆘 Common Issues

### Tests Fail with "Connection Refused"

**Solution:** Ensure the app is running:
```bash
python main.py &
# or
docker-compose up -d
```

### LLM Tests Timeout

**Solution:** Increase timeout or use mock:
```python
async with AsyncClient(app=app, timeout=180.0) as client:
    ...
```

### PDF Tests Fail

**Solution:** Check matplotlib backend:
```python
import matplotlib
matplotlib.use('Agg')
```

---

**Happy Testing! 🧪**
