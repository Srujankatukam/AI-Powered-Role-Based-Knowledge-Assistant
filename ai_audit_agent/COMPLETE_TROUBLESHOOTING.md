# 🔧 Complete Troubleshooting - Nothing Working

You reported:
- ❌ Not sending emails
- ❌ Not triggered from form submission
- ❌ No PDF generated

Let's diagnose and fix everything step by step.

---

## 🚨 IMMEDIATE DIAGNOSTIC

Run this RIGHT NOW:

```bash
cd ai_audit_agent
python diagnose_full_workflow.py
```

This will test:
1. Environment configuration
2. LLM client (Ollama or HuggingFace)
3. PDF generation
4. Email service
5. API endpoint
6. Full webhook workflow

**Share the complete output!**

---

## 🔍 Quick Checks (Do These First)

### Check 1: Is the Application Running?

```bash
# Test health endpoint
curl http://localhost:8000/health
```

**✅ If working:**
```json
{"status":"ok","timestamp":"...","service":"AI Audit Agent"}
```

**❌ If not:**
```
curl: (7) Failed to connect to localhost port 8000
```

**Fix:** Start the application
```bash
python main.py
# OR
docker-compose up
```

---

### Check 2: Is Your .env Configured?

```bash
cat .env
```

**Required for Ollama:**
```bash
USE_OLLAMA=true
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434

SENDER_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

**Required for Hugging Face:**
```bash
USE_OLLAMA=false
HF_API_KEY=hf_your_key_here

SENDER_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

**If .env doesn't exist:**
```bash
cp .env.example .env
nano .env
# Add your credentials
```

---

### Check 3: Is Ollama Running? (If Using Ollama)

```bash
curl http://localhost:11434
```

**✅ Should return:**
```
Ollama is running
```

**❌ If error:**
```bash
# Start Ollama in terminal 1
ollama serve

# Download model in terminal 2
ollama pull llama3
```

---

### Check 4: Are Email Credentials Set?

```bash
# Check .env
cat .env | grep -E "SENDER_EMAIL|SMTP_PASSWORD"
```

**Must show:**
```
SENDER_EMAIL=your-actual-email@gmail.com
SMTP_PASSWORD=your_actual_app_password
```

**NOT:**
```
SENDER_EMAIL=your-email@gmail.com  ❌ (example)
SMTP_PASSWORD=your_gmail_app_password_here  ❌ (example)
```

**Get Gmail app password:**
1. Go to https://myaccount.google.com/apppasswords
2. Generate new app password
3. Add to .env

---

## 🔬 Detailed Diagnostics

### Step 1: Check Application Logs

**If running directly:**
```bash
python main.py
```

Watch the output when you send a request.

**If using Docker:**
```bash
docker-compose logs -f
```

---

### Step 2: Send Test Request & Watch Logs

**Terminal 1: Watch logs**
```bash
python main.py
# OR
docker-compose logs -f
```

**Terminal 2: Send test request**
```bash
curl -X POST http://localhost:8000/webhook/sheet-row \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Company",
    "recipient_name": "Your Name",
    "recipient_email": "your-email@gmail.com",
    "industry": "Technology",
    "company_size": "Small",
    "annual_revenue_inr": "10 Cr",
    "departments": {"IT": {"website": "Basic"}}
  }'
```

---

### What to Look For in Logs:

**✅ GOOD (Working):**
```
INFO: Started server process
INFO: Application startup complete
INFO: [audit_xxx] Starting audit processing for Test Company
INFO: [audit_xxx] Calling LLM for analysis...
INFO: [audit_xxx] LLM analysis completed successfully
INFO: [audit_xxx] Generating PDF report...
INFO: [audit_xxx] PDF generated at: /tmp/AI_Audit_...
INFO: [audit_xxx] Sending email to your-email@gmail.com...
INFO: [audit_xxx] Email sent successfully
INFO: [audit_xxx] Audit processing completed successfully
```

**❌ BAD (Failing):**
```
ERROR: Cannot connect to Ollama
ERROR: HF_API_KEY not found
ERROR: SMTP authentication failed
ERROR: Failed to send email
WARNING: Email service is not enabled
```

---

## 🐛 Common Issues & Fixes

### Issue 1: "Email service is not enabled"

**Logs show:**
```
WARNING: Email credentials not configured
WARNING: Email service is not enabled. Skipping email send.
```

**Cause:** `.env` missing email settings

**Fix:**
```bash
nano .env

# Add these with YOUR actual credentials:
SENDER_EMAIL=your-real-email@gmail.com
SMTP_PASSWORD=your-real-app-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465

# Restart
python main.py
```

---

### Issue 2: "Cannot connect to Ollama"

**Logs show:**
```
ERROR: Cannot connect to Ollama at http://localhost:11434
```

**Cause:** Ollama not running

**Fix:**
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Download model (if not downloaded)
ollama pull llama3

# Terminal 3: Restart app
python main.py
```

---

### Issue 3: "Background task not executing"

**Logs show webhook accepted but nothing after:**
```
INFO: [audit_xxx] Received audit request for Company
(nothing more)
```

**Cause:** Background task silently failing

**Fix:**
```bash
# Run in foreground to see errors
python main.py

# Check for exceptions in background task
# Look for ERROR or WARNING messages
```

---

### Issue 4: "SMTP authentication failed"

**Logs show:**
```
ERROR: SMTP authentication failed. Check email credentials.
```

**Causes:**
1. Using regular Gmail password (not app password)
2. 2-Step Verification not enabled
3. Wrong password

**Fix:**
1. Enable 2-Step: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use app password in .env (not your regular password)

---

### Issue 5: "PDF file not created"

**Logs show:**
```
ERROR: Error creating PDF report
```

**Causes:**
1. Missing matplotlib/reportlab
2. No write permissions to /tmp
3. Invalid data

**Fix:**
```bash
# Install dependencies
pip install -r requirements.txt

# Test PDF creation
python -c "from pdf_builder import PDFBuilder; print('PDF Builder OK')"

# Check /tmp permissions
ls -la /tmp | head
```

---

## 🎯 Step-by-Step Fix Guide

### Step 1: Create Proper .env

```bash
cd ai_audit_agent

# Copy example
cp .env.example .env

# Edit with YOUR credentials
nano .env
```

**For Ollama (Recommended):**
```bash
# LLM Configuration
USE_OLLAMA=true
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434

# Email Configuration (REPLACE WITH YOUR REAL CREDENTIALS!)
SENDER_EMAIL=your-actual-email@gmail.com
SMTP_PASSWORD=your-actual-app-password-here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
```

---

### Step 2: Start Ollama (If Using Ollama)

**Terminal 1:**
```bash
ollama serve
```

**Terminal 2:**
```bash
# Check if llama3 is downloaded
ollama list

# If not downloaded:
ollama pull llama3
```

---

### Step 3: Start Application

```bash
cd ai_audit_agent
python main.py
```

**Watch for:**
```
INFO: Using Ollama - Model: llama3 at http://localhost:11434
INFO: Email service initialized with sender: your-email@gmail.com
INFO: Application startup complete
INFO: Uvicorn running on http://0.0.0.0:8000
```

**NOT:**
```
WARNING: Email credentials not configured
WARNING: Email service will be disabled
```

---

### Step 4: Test Full Workflow

**In another terminal:**
```bash
python test_api_directly.py
```

**Watch the first terminal (where main.py is running)**

You should see:
```
INFO: [audit_xxx] Starting audit processing
INFO: [audit_xxx] Calling LLM...
INFO: [audit_xxx] LLM analysis completed
INFO: [audit_xxx] Generating PDF...
INFO: [audit_xxx] PDF generated
INFO: [audit_xxx] Sending email...
INFO: [audit_xxx] Email sent successfully
```

---

### Step 5: Check Email

Wait 60 seconds, then check:
- Inbox
- Spam folder
- Promotions tab (Gmail)

---

## 📊 Verification Checklist

Run through this checklist:

- [ ] `.env` file exists and has real credentials
- [ ] `USE_OLLAMA=true` in .env (if using Ollama)
- [ ] Ollama is running (`curl http://localhost:11434`)
- [ ] Model is downloaded (`ollama list | grep llama3`)
- [ ] Email credentials are REAL (not example values)
- [ ] Application started successfully (`python main.py`)
- [ ] Health endpoint works (`curl http://localhost:8000/health`)
- [ ] Logs show "Email service initialized" (not "disabled")
- [ ] Test request sent successfully
- [ ] Logs show background processing started
- [ ] Email received within 60 seconds

---

## 🚀 Complete Setup from Scratch

If nothing works, start fresh:

```bash
cd ai_audit_agent

# 1. Setup Ollama
bash setup_ollama.sh

# 2. Configure .env
cp .env.example .env
nano .env

# Add these with YOUR real values:
USE_OLLAMA=true
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434

SENDER_EMAIL=your-actual-email@gmail.com
SMTP_PASSWORD=your-actual-app-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465

# Save (Ctrl+O, Enter, Ctrl+X)

# 3. Start Ollama (if not running)
ollama serve &

# 4. Start application
python main.py

# 5. In another terminal, test
python test_api_directly.py

# 6. Check email in 60 seconds
```

---

## 🔍 Debug Mode

Run with debug logging:

```bash
# Edit main.py temporarily
# Change line ~20 from:
level=logging.INFO

# To:
level=logging.DEBUG

# Restart and watch logs
python main.py
```

This shows much more detail about what's happening.

---

## 📞 Share This Info

If still not working, share:

1. **Output of:**
   ```bash
   python diagnose_full_workflow.py
   ```

2. **Your .env (HIDE passwords):**
   ```bash
   cat .env | sed 's/=.*/=HIDDEN/'
   ```

3. **Application logs** when you send a test request

4. **Specific error messages** you see

---

## 💡 Most Common Causes

**90% of "nothing works" issues:**

1. ❌ `.env` has example values (not real credentials)
2. ❌ Application not running
3. ❌ Ollama not running (if using Ollama)
4. ❌ Email credentials wrong

**Check these first!**

---

**Run `python diagnose_full_workflow.py` and share the output!**

---

*Last Updated: 2024-11-05*
