# 🚨 NOTHING IS WORKING - URGENT FIX GUIDE

You reported:
- ❌ Not sending emails
- ❌ Not getting triggered for form submission  
- ❌ No PDF being generated

## 🎯 IMMEDIATE ACTION - DO THIS NOW

### Step 1: Run Quick Status Check

```bash
cd ai_audit_agent
python quick_status.py
```

**This will tell you EXACTLY what's wrong!**

Share the output with me if you need help interpreting it.

---

## 🔥 Most Likely Issues (90% of cases)

### Issue #1: Application Not Running ⚠️

**Check:**
```bash
curl http://localhost:8000/health
```

**If you get connection error:**
```bash
# Start the application
cd ai_audit_agent
python main.py
```

**Keep this terminal open!** Watch the logs when you submit the form.

---

### Issue #2: Email Credentials Not Configured ⚠️

**Check your .env file:**
```bash
cat .env | grep -E "SENDER_EMAIL|SMTP_PASSWORD"
```

**If it shows example values like:**
```bash
SENDER_EMAIL=your-email@gmail.com  ❌ WRONG
SMTP_PASSWORD=your_gmail_app_password_here  ❌ WRONG
```

**Fix it NOW:**
```bash
nano .env

# Change to YOUR real credentials:
SENDER_EMAIL=your-actual-email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop  # Your Gmail app password

# Save: Ctrl+O, Enter, Ctrl+X
```

**Get Gmail App Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Generate new password
3. Copy the 16-character password
4. Paste into .env (spaces are OK)

---

### Issue #3: Ollama Not Running ⚠️

**If using Ollama, check:**
```bash
curl http://localhost:11434
```

**If error, start Ollama:**
```bash
# Terminal 1 (keep open)
ollama serve

# Terminal 2
ollama pull llama3
```

---

### Issue #4: Wrong Webhook URL in Google Sheets ⚠️

**Check your Google Apps Script:**

The `WEBHOOK_URL` must point to where your app is ACTUALLY running:

```javascript
// WRONG - if running locally
const WEBHOOK_URL = "https://10.246.184.25:8000/webhook/sheet-row";

// CORRECT - for local development
const WEBHOOK_URL = "http://localhost:8000/webhook/sheet-row";

// OR use your actual local IP
const WEBHOOK_URL = "http://10.246.184.25:8000/webhook/sheet-row";
```

---

## 📋 Complete Checklist

Run through this checklist:

- [ ] `.env` file exists and has REAL credentials (not examples)
- [ ] Application is running (`python main.py` in a terminal)
- [ ] Terminal shows "Application startup complete"
- [ ] Health check works: `curl http://localhost:8000/health`
- [ ] If using Ollama: `ollama serve` is running
- [ ] If using Ollama: Model downloaded: `ollama list`
- [ ] Email credentials are REAL Gmail app password
- [ ] Google Sheets webhook URL points to correct address

---

## 🧪 Test the Full Workflow

Once checklist is complete:

### Terminal 1: Watch Logs
```bash
cd ai_audit_agent
python main.py
# Keep watching this terminal!
```

### Terminal 2: Send Test Request
```bash
cd ai_audit_agent
python test_api_directly.py
```

### What You Should See in Terminal 1:

```
INFO: [audit_xxx] Received audit request for Test Company
INFO: [audit_xxx] Starting audit processing for Test Company
INFO: [audit_xxx] Calling LLM for analysis...
INFO: [audit_xxx] LLM analysis completed successfully
INFO: [audit_xxx] Generating PDF report...
INFO: [audit_xxx] PDF generated at: /tmp/AI_Audit_...
INFO: [audit_xxx] Sending email to test@email.com...
INFO: [audit_xxx] Email sent successfully
INFO: [audit_xxx] Audit processing completed successfully
```

**NOT:**
```
WARNING: Email service is not enabled  ❌
ERROR: Cannot connect to Ollama  ❌
ERROR: SMTP authentication failed  ❌
```

---

## 🔍 Advanced Debugging

If still not working after the above, run full diagnostic:

```bash
cd ai_audit_agent
python diagnose_full_workflow.py
```

This tests EVERYTHING:
- Environment variables
- LLM client (Ollama or HuggingFace)
- PDF generation
- Email service
- SMTP connection
- Full webhook workflow

Share the complete output!

---

## 💡 Common Mistakes

### Mistake 1: Using example .env values
```bash
# BAD - these are examples!
SENDER_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your_gmail_app_password_here

# GOOD - real values
SENDER_EMAIL=john.doe@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
```

### Mistake 2: Using regular Gmail password
```bash
# BAD - regular password doesn't work!
SMTP_PASSWORD=MyGmail123!

# GOOD - app password from Google
SMTP_PASSWORD=abcd efgh ijkl mnop
```

### Mistake 3: Application not running
```bash
# Check if running:
curl http://localhost:8000/health

# If error, START IT:
python main.py
```

### Mistake 4: Wrong directory
```bash
# Make sure you're in the right place!
cd ai_audit_agent
pwd
# Should show: /path/to/ai_audit_agent
```

---

## 🆘 Still Not Working?

Run these commands and share ALL output:

```bash
# 1. Quick status
cd ai_audit_agent
python quick_status.py

# 2. Check .env (HIDE passwords)
cat .env | sed 's/=.*/=HIDDEN/'

# 3. Check if app running
curl http://localhost:8000/health

# 4. Check Ollama (if using)
curl http://localhost:11434

# 5. Full diagnostic
python diagnose_full_workflow.py
```

---

## ⚡ Quick Fix - Start Fresh

If everything is confusing, start completely fresh:

```bash
cd ai_audit_agent

# 1. Stop everything
# Press Ctrl+C in any terminals running python or ollama

# 2. Fix .env with REAL credentials
nano .env
# Add your real email and app password
# Save and exit

# 3. Start Ollama (if using)
ollama serve &
ollama pull llama3

# 4. Start application
python main.py
# KEEP THIS RUNNING!

# 5. In another terminal, test
python test_api_directly.py

# 6. Check email in 60 seconds
```

---

## 📧 Email Troubleshooting Specific

If ONLY email is not working:

### Test SMTP Connection
```bash
cd ai_audit_agent
python -c "
from mailer import EmailService
import logging
logging.basicConfig(level=logging.INFO)
service = EmailService()
print('Enabled:', service.enabled)
if service.enabled:
    result = service.test_connection()
    print('Connection Test:', 'PASS ✅' if result else 'FAIL ❌')
"
```

**Should show:**
```
Enabled: True
Connection Test: PASS ✅
```

**NOT:**
```
Enabled: False  ❌
WARNING: Email credentials not configured  ❌
```

---

## 🎯 Action Plan

1. **RIGHT NOW:** Run `python quick_status.py`
2. **Fix** any issues it reports
3. **Restart** the application if you changed .env
4. **Test** with `python test_api_directly.py`
5. **Watch** the terminal logs
6. **Check** email in 60 seconds

---

**Most issues are fixed by:**
1. Setting REAL email credentials in .env
2. Actually starting the application (python main.py)
3. Starting Ollama if using it (ollama serve)

**DO THESE THREE THINGS FIRST!**
