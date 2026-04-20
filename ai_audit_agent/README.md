# AI Audit Agent 🤖

A comprehensive FastAPI application that performs automated AI audits for organizations, generating detailed reports with visualizations and delivering them via email.

## 🌟 Features

- **Automated Audit Workflow**: Triggered by Google Sheets webhook
- **AI-Powered Analysis**: Uses Mistral-7B-Instruct-v0.1 (Hugging Face) for intelligent analysis
- **PDF Report Generation**: Beautiful reports with company details and insights
- **Data Visualizations**: 
  - AI Maturity Bar Chart (department-wise)
  - Risk Radar Chart (multi-dimensional view)
- **Email Delivery**: Automatic email sending with PDF attachment
- **Personalized Summaries**: Context-aware executive summaries
- **Comprehensive Logging**: Full audit trail with timestamps

## 🏗️ Architecture

```
Google Sheets → Apps Script → Webhook → FastAPI → LLM → PDF Builder → Email Service
```

## 📋 Prerequisites

- Python 3.11+
- Hugging Face API key
- Gmail account with App Password
- Docker (optional)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Create project directory
mkdir ai_audit_agent
cd ai_audit_agent

# Copy all Python files to this directory
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required Environment Variables:**

- `HF_API_KEY`: Your Hugging Face API key ([Get it here](https://huggingface.co/settings/tokens))
- `SENDER_EMAIL`: Your Gmail address
- `SMTP_PASSWORD`: Gmail App Password ([Instructions](https://support.google.com/accounts/answer/185833))

### 4. Run the Application

```bash
# Development mode
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 5. Test the Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00",
  "service": "AI Audit Agent"
}
```

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t ai-audit-agent .
```

### Run Container

```bash
docker run -d \
  --name ai-audit-agent \
  -p 8000:8000 \
  -e HF_API_KEY=your_key_here \
  -e SENDER_EMAIL=your_email@gmail.com \
  -e SMTP_PASSWORD=your_app_password \
  ai-audit-agent
```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  ai-audit-agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HF_API_KEY=${HF_API_KEY}
      - SENDER_EMAIL=${SENDER_EMAIL}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - SMTP_HOST=smtp.gmail.com
      - SMTP_PORT=465
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

Run with:
```bash
docker-compose up -d
```

## 📊 API Endpoints

### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "service": "AI Audit Agent"
}
```

### 2. Webhook (Google Sheets Trigger)
```http
POST /webhook/sheet-row
Content-Type: application/json
```

**Request Body:**
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
      "competitor_analysis_frequency": "Quarterly"
    },
    "Customer Engagement": {
      "inquiry_handling": "Email/calls manually",
      "collect_feedback": "Collected but not analyzed",
      "avg_response_time": "12-24 hours"
    },
    "Human Resources": {
      "recruitment_screening": "Basic filtering",
      "attendance_tracking": "Manual register"
    },
    "IT & Technology": {
      "website": "Dynamic website",
      "backup_security": "Scheduled backup"
    }
  }
}
```

**Response:**
```json
{
  "status": "accepted",
  "message": "Audit request accepted and being processed for NovaTech Industries",
  "request_id": "audit_20240115_103000",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## 📧 Email Configuration

### Gmail Setup

1. **Enable 2-Step Verification**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification

2. **Generate App Password**
   - Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and your device
   - Generate password
   - Use this password in `SMTP_PASSWORD`

### Email Format

The system sends HTML emails with:
- Professional formatting
- Executive summary
- Company details
- PDF attachment
- Branded footer

## 🔗 Google Sheets Integration

See `docs/gs_script.txt` for the complete Google Apps Script code.

### Setup Steps:

1. **Open Your Google Sheet**

2. **Open Script Editor**
   - Extensions → Apps Script

3. **Paste the Script**
   - Copy code from `docs/gs_script.txt`
   - Replace `YOUR_API_URL` with your server URL

4. **Add Trigger**
   - Click on clock icon (Triggers)
   - Add Trigger:
     - Function: `onFormSubmit` or `onEdit`
     - Event source: From spreadsheet
     - Event type: On form submit / On edit
   - Save

5. **Test**
   - Add a new row to your sheet
   - Check server logs for webhook receipt

## 📄 PDF Report Contents

Generated reports include:

1. **Cover Page**
   - Company name and details
   - Report date
   - Recipient information

2. **Executive Summary**
   - Personalized analysis paragraph
   - AI Maturity Level
   - Overall Risk Score

3. **Visualizations**
   - Bar Chart: Department-wise AI maturity
   - Radar Chart: Risk distribution

4. **Detailed Analysis**
   - Department-by-department breakdown
   - Specific drawbacks and limitations
   - Evidence-based insights

5. **Footer**
   - Generation timestamp
   - Confidentiality notice

## 🧪 Testing

### Manual Testing with cURL

```bash
curl -X POST http://localhost:8000/webhook/sheet-row \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Corp",
    "recipient_name": "John Doe",
    "recipient_email": "john@testcorp.com",
    "industry": "Technology",
    "company_size": "Medium (51-200 employees)",
    "annual_revenue_inr": "100 Cr",
    "departments": {
      "IT": {
        "infrastructure": "Cloud-based"
      }
    }
  }'
```

### Automated Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## 📁 Project Structure

```
ai_audit_agent/
├── main.py                 # FastAPI application
├── llm_client.py          # Hugging Face LLM client
├── pdf_builder.py         # PDF generation with charts
├── mailer.py              # Email service
├── prompt_templates.py    # LLM prompts
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── .env.example          # Environment template
├── README.md             # This file
└── docs/
    └── gs_script.txt     # Google Apps Script
```

## 🔍 Logging

Logs include:
- Request receipts
- LLM API calls
- PDF generation
- Email delivery
- Errors and exceptions

**View logs:**
```bash
# If running directly
tail -f app.log

# If using Docker
docker logs -f ai-audit-agent
```

## 🛠️ Troubleshooting

### LLM API Errors

**Problem:** 503 Service Unavailable

**Solution:** Model is loading. Wait 20-30 seconds and retry.

**Problem:** 401 Unauthorized

**Solution:** Check `HF_API_KEY` in `.env`

### Email Delivery Issues

**Problem:** SMTP Authentication Failed

**Solution:** 
- Verify Gmail App Password (not your regular password)
- Ensure 2-Step Verification is enabled
- Check `SENDER_EMAIL` and `SMTP_PASSWORD`

**Problem:** Email not received

**Solution:**
- Check spam folder
- Verify recipient email
- Review logs for SMTP errors

### PDF Generation Errors

**Problem:** Charts not displaying

**Solution:**
- Ensure matplotlib is installed: `pip install matplotlib`
- Check write permissions for `/tmp`

### Webhook Issues

**Problem:** Google Sheets trigger not working

**Solution:**
- Verify webhook URL is publicly accessible
- Check Apps Script logs
- Test webhook manually with cURL

## 🔐 Security Considerations

1. **API Keys**: Never commit `.env` file to version control
2. **HTTPS**: Use SSL/TLS in production
3. **Authentication**: Add API key authentication for webhook endpoint
4. **Rate Limiting**: Implement rate limiting for production
5. **Input Validation**: Pydantic models provide built-in validation

## 📈 Performance

- **Average Processing Time**: 30-60 seconds per audit
- **LLM Response Time**: 10-30 seconds
- **PDF Generation**: 5-10 seconds
- **Email Delivery**: 2-5 seconds

## 🚀 Production Deployment

### Recommended Setup

1. **Use a Production WSGI Server**
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

2. **Add Nginx Reverse Proxy**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Enable SSL with Let's Encrypt**
   ```bash
   certbot --nginx -d your-domain.com
   ```

4. **Set Up Monitoring**
   - Use PM2, systemd, or Docker Compose
   - Enable health check monitoring
   - Set up log aggregation

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Check the [Troubleshooting](#-troubleshooting) section
- Review logs for error messages
- Open an issue on GitHub

## 🎯 Roadmap

- [ ] Add support for multiple LLM providers
- [ ] Implement caching for repeated analyses
- [ ] Add user dashboard for report history
- [ ] Support for custom report templates
- [ ] Multi-language support
- [ ] Real-time progress updates via WebSocket

## 📞 Contact

For questions or support, contact: your-email@domain.com

---

**Built with ❤️ using FastAPI, Hugging Face, and Python**
