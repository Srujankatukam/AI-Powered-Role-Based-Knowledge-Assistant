# AI Audit Agent - API Documentation

## Overview

The AI Audit Agent provides a REST API for automated AI audit report generation. This document describes all available endpoints, request/response formats, and integration guidelines.

## Base URL

```
http://localhost:8000     # Development
https://your-domain.com   # Production
```

## API Endpoints

### 1. Health Check

Check if the service is running and healthy.

**Endpoint:** `GET /health`

**Response:** `200 OK`

```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00.123456",
  "service": "AI Audit Agent"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### 2. Root Endpoint

Alternative health check endpoint.

**Endpoint:** `GET /`

**Response:** `200 OK`

```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00.123456",
  "service": "AI Audit Agent"
}
```

---

### 3. Webhook - Process Audit Request

Main endpoint for triggering audit report generation. Typically called by Google Apps Script.

**Endpoint:** `POST /webhook/sheet-row`

**Headers:**
```
Content-Type: application/json
```

**Request Body Schema:**

```json
{
  "company_name": "string (required, min_length: 1)",
  "recipient_name": "string (required, min_length: 1)",
  "recipient_email": "string (required, valid email)",
  "industry": "string (required)",
  "company_size": "string (required)",
  "annual_revenue_inr": "string (required)",
  "departments": {
    "Department Name": {
      "field_name": "field_value",
      ...
    },
    ...
  }
}
```

**Request Body Example:**

```json
{
  "company_name": "NovaTech Industries",
  "recipient_name": "Ananya Mehta",
  "recipient_email": "ananya@novatech.com",
  "industry": "Manufacturing",
  "company_size": "Large (201-1000 employees)",
  "annual_revenue_inr": "250 Cr",
  "departments": {
    "Leadership & Management": {
      "track_business_metrics": "Excel spreadsheets",
      "competitor_analysis_frequency": "Quarterly",
      "decision_making_process": "Manual analysis"
    },
    "Customer Engagement": {
      "inquiry_handling": "Email/calls manually",
      "collect_feedback": "Collected but not analyzed",
      "avg_response_time": "12-24 hours",
      "crm_system": "Basic contact management"
    },
    "Human Resources": {
      "recruitment_screening": "Basic filtering",
      "attendance_tracking": "Manual register",
      "performance_reviews": "Annual paper-based"
    },
    "IT & Technology": {
      "website": "Dynamic website",
      "backup_security": "Scheduled backup",
      "infrastructure": "Mix of on-premise and cloud"
    },
    "Operations": {
      "inventory_management": "Excel-based tracking",
      "quality_control": "Manual inspection",
      "supply_chain": "Email-based coordination"
    }
  }
}
```

**Success Response:** `200 OK`

```json
{
  "status": "accepted",
  "message": "Audit request accepted and being processed for NovaTech Industries",
  "request_id": "audit_20240115_103000",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

**Error Responses:**

**Validation Error:** `422 Unprocessable Entity`

```json
{
  "detail": [
    {
      "loc": ["body", "recipient_email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

**Server Error:** `500 Internal Server Error`

```json
{
  "status": "error",
  "message": "Internal server error occurred",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

---

## Request Validation Rules

### Required Fields

All of the following fields are required:

- `company_name` - Must not be empty
- `recipient_name` - Must not be empty
- `recipient_email` - Must be a valid email address
- `industry` - Company's industry sector
- `company_size` - Size category of the company
- `annual_revenue_inr` - Annual revenue (any format)
- `departments` - Object containing at least one department

### Department Structure

- Each department is a key-value pair
- Department name is the key (string)
- Department data is an object with flexible fields
- At least one department must be provided

---

## Background Processing

The webhook endpoint returns immediately after validation. Processing happens asynchronously in the background:

1. **LLM Analysis** - Sends data to Mistral-7B-Instruct-v0.1 for analysis (~10-30 seconds)
2. **PDF Generation** - Creates report with visualizations (~5-10 seconds)
3. **Email Delivery** - Sends report to recipient (~2-5 seconds)

Total processing time: **30-60 seconds**

---

## Integration Examples

### Python

```python
import requests
import json

url = "http://localhost:8000/webhook/sheet-row"

data = {
    "company_name": "TechCorp Inc",
    "recipient_name": "Jane Doe",
    "recipient_email": "jane@techcorp.com",
    "industry": "Technology",
    "company_size": "Medium (51-200 employees)",
    "annual_revenue_inr": "150 Cr",
    "departments": {
        "IT": {
            "infrastructure": "Cloud-based",
            "automation_level": "Medium"
        },
        "HR": {
            "recruitment": "ATS-based",
            "onboarding": "Semi-automated"
        }
    }
}

response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    print(f"Success! Request ID: {result['request_id']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const url = 'http://localhost:8000/webhook/sheet-row';

const data = {
  company_name: 'TechCorp Inc',
  recipient_name: 'Jane Doe',
  recipient_email: 'jane@techcorp.com',
  industry: 'Technology',
  company_size: 'Medium (51-200 employees)',
  annual_revenue_inr: '150 Cr',
  departments: {
    IT: {
      infrastructure: 'Cloud-based',
      automation_level: 'Medium'
    },
    HR: {
      recruitment: 'ATS-based',
      onboarding: 'Semi-automated'
    }
  }
};

axios.post(url, data)
  .then(response => {
    console.log('Success!', response.data);
  })
  .catch(error => {
    console.error('Error:', error.response?.data || error.message);
  });
```

### cURL

```bash
curl -X POST http://localhost:8000/webhook/sheet-row \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "TechCorp Inc",
    "recipient_name": "Jane Doe",
    "recipient_email": "jane@techcorp.com",
    "industry": "Technology",
    "company_size": "Medium (51-200 employees)",
    "annual_revenue_inr": "150 Cr",
    "departments": {
      "IT": {
        "infrastructure": "Cloud-based"
      }
    }
  }'
```

---

## Error Handling

### Common Error Codes

| Code | Description | Cause |
|------|-------------|-------|
| 200 | Success | Request processed successfully |
| 422 | Validation Error | Invalid request format or missing required fields |
| 500 | Server Error | Internal processing error (LLM, PDF, or email failure) |

### Best Practices

1. **Always check response status**
   ```python
   if response.status_code == 200:
       # Success
   else:
       # Handle error
   ```

2. **Log request_id for tracking**
   ```python
   request_id = response.json().get('request_id')
   logger.info(f"Audit initiated: {request_id}")
   ```

3. **Implement retry logic for 500 errors**
   ```python
   max_retries = 3
   for attempt in range(max_retries):
       response = requests.post(url, json=data)
       if response.status_code == 200:
           break
       time.sleep(2 ** attempt)  # Exponential backoff
   ```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider:

- Maximum 100 requests per hour per IP
- Maximum 1000 requests per day per organization
- Implement API keys for tracking and limiting

---

## Authentication

Currently, the API is open. For production, implement:

- API key authentication
- JWT tokens
- IP whitelisting

Example with API key:

```bash
curl -X POST http://localhost:8000/webhook/sheet-row \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{...}'
```

---

## Monitoring and Logging

All requests are logged with:

- Timestamp
- Request ID
- Company name
- Processing stages
- Success/failure status

Check logs:

```bash
# Direct run
tail -f app.log

# Docker
docker logs -f ai-audit-agent
```

---

## Support

For API issues:

1. Check application logs
2. Verify request format matches schema
3. Ensure all environment variables are configured
4. Test with the health endpoint first

---

## Changelog

### Version 1.0.0 (2024-01)

- Initial release
- POST /webhook/sheet-row endpoint
- GET /health endpoint
- Async background processing
- PDF generation with visualizations
- Email delivery integration
