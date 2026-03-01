# AI Audit Agent - Quick Start Guide

Get up and running in 5 minutes! ⚡

## 🎯 What You Need

1. **Hugging Face Account** - [Sign up here](https://huggingface.co)
2. **Gmail Account** - For sending reports
3. **Docker** (Optional) - For containerized deployment

---

## ⚡ 5-Minute Setup

### Step 1: Get Your API Keys (2 minutes)

**Hugging Face API Key:**
1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Copy your token

**Gmail App Password:**
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to https://myaccount.google.com/apppasswords
4. Generate new app password
5. Copy the password

### Step 2: Configure Environment (1 minute)

```bash
cd ai_audit_agent
cp .env.example .env
```

Edit `.env`:
```bash
HF_API_KEY=hf_your_key_here
SENDER_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your_app_password_here
```

### Step 3: Run the Application (2 minutes)

**Option A: Using Docker (Recommended)**
```bash
docker-compose up -d
```

**Option B: Using Python**
```bash
pip install -r requirements.txt
python main.py
```

### Step 4: Test It! (30 seconds)

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{"status":"ok","timestamp":"...","service":"AI Audit Agent"}
```

---

## 🧪 Test with Sample Data

Run the test script:
```bash
python test_example.py
```

Or manually:
```bash
curl -X POST http://localhost:8000/webhook/sheet-row \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Demo Corp",
    "recipient_name": "Your Name",
    "recipient_email": "your-email@gmail.com",
    "industry": "Technology",
    "company_size": "Medium",
    "annual_revenue_inr": "100 Cr",
    "departments": {
      "IT": {"infrastructure": "Cloud-based"}
    }
  }'
```

Check your email in ~60 seconds for the report!

---

## 🔗 Connect Google Sheets

### 1. Open Your Google Sheet

### 2. Add Required Columns (Row 1)
- Company Name
- Recipient Name  
- Recipient Email
- Industry
- Company Size
- Annual Revenue (INR)
- L&M: Track Business Metrics
- CE: Inquiry Handling
- HR: Recruitment Screening
- IT: Website

### 3. Setup Apps Script

1. Extensions → Apps Script
2. Copy code from `docs/gs_script.txt`
3. Replace `YOUR_API_URL` with your server URL
4. Save

### 4. Add Trigger

1. Click clock icon (Triggers)
2. Add Trigger
3. Function: `onEdit`
4. Event: On edit
5. Save

### 5. Test

Add a new row to your sheet → Email arrives automatically!

---

## 📊 What Happens Next?

1. **Immediate Response** - Webhook returns request ID
2. **LLM Analysis** (~15-30s) - AI analyzes your data
3. **PDF Generation** (~5-10s) - Creates professional report
4. **Email Delivery** (~2-5s) - Sends to recipient

**Total time: ~30-60 seconds**

---

## 🎉 You're Done!

You now have:
- ✅ Working AI Audit Agent
- ✅ Automated report generation
- ✅ Email delivery
- ✅ Google Sheets integration

---

## 🆘 Common Issues

**Issue:** Health check fails
```bash
# Check if app is running
docker-compose ps

# View logs
docker-compose logs -f
```

**Issue:** LLM timeout
```bash
# Wait for model to load (first request takes longer)
# Retry after 30 seconds
```

**Issue:** Email not received
```bash
# Check spam folder
# Verify credentials in .env
# Test connection: python test_example.py
```

---

## 📚 Next Steps

- 📖 Read [README.md](README.md) for full documentation
- 🚀 See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for production setup
- 🧪 Check [TESTING_GUIDE.md](docs/TESTING_GUIDE.md) for testing
- 📡 Review [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for API details

---

## 💡 Example Use Cases

1. **Regular Audits** - Schedule monthly audits via Google Sheets
2. **Client Assessments** - Generate reports for new clients
3. **Internal Reviews** - Assess department readiness
4. **Competitive Analysis** - Track AI maturity over time

---

## 🌟 Pro Tips

- **Use Docker** for easier deployment
- **Check logs** if something goes wrong
- **Test with dummy data** before production
- **Setup monitoring** for production use
- **Keep API keys secure** - never commit .env

---

**Need Help?** Check the full [README.md](README.md) or review logs!

**Ready for Production?** See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)!

---

**Happy Auditing! 🎯**
